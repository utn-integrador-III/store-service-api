
from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument


COLL = "reviews"
BUSINESSES = "businesses"



def _to_oid(x: Any) -> Optional[ObjectId]:
    """Convierte a ObjectId si es posible."""
    try:
        return ObjectId(str(x))
    except Exception:
        return None


def _id_choices(value: Any) -> List[Any]:
    """
    Devuelve una lista con ambas representaciones (str y ObjectId) para usar en $in.
    Si no se puede convertir a OID, queda solo el str.
    """
    out: List[Any] = []
    s = str(value) if value is not None else None
    if s:
        out.append(s)
        oid = _to_oid(s)
        if oid is not None:
            out.append(oid)
    return out



async def get_reviews_by_business(db: AsyncIOMotorDatabase, business_id: str) -> List[Dict[str, Any]]:
    ids = _id_choices(business_id)
    reviews = (
        await db[COLL]
        .find({"business_id": {"$in": ids}})
        .sort("created_at", -1)
        .to_list(length=1000)
    )
    return reviews


async def get_user_review_for_appointment(
    db: AsyncIOMotorDatabase, user_id: str, appointment_id: str
) -> Optional[Dict[str, Any]]:
    ids = _id_choices(appointment_id)
    return await db[COLL].find_one({"user_id": user_id, "appointment_id": {"$in": ids}})



async def create_review(
    db: AsyncIOMotorDatabase,
    *,
    business_id: str,
    appointment_id: str,
    user_id: str,
    rating: int,
    comment: str = "",
) -> Dict[str, Any]:
    now = datetime.utcnow()
    doc = {
        "business_id": business_id,
        "appointment_id": appointment_id,
        "user_id": user_id,
        "rating": int(rating),
        "comment": comment or "",
        "created_at": now,
        "updated_at": now,
    }
    res = await db[COLL].insert_one(doc)
    doc["_id"] = res.inserted_id
    return doc


async def update_review(
    db: AsyncIOMotorDatabase,
    review_id: str,
    user_id: str,
    data: Dict[str, Any],
) -> Optional[Dict[str, Any]]:

    data = {**data, "updated_at": datetime.utcnow()}
    return await db[COLL].find_one_and_update(
        {"_id": _to_oid(review_id), "user_id": user_id},
        {"$set": data},
        return_document=ReturnDocument.AFTER,
    )


async def delete_review(db: AsyncIOMotorDatabase, review_id: str, user_id: str) -> bool:
    res = await db[COLL].delete_one({"_id": _to_oid(review_id), "user_id": user_id})
    return res.deleted_count > 0


async def add_reply(
    db: AsyncIOMotorDatabase,
    *,
    review_id: str,
    author_role: str,
    author_id: str,
    content: str,
) -> Dict[str, Any]:
    now = datetime.utcnow()
    reply = {"text": content, "role": author_role, "created_at": now, "author_id": author_id}
    doc = await db[COLL].find_one_and_update(
        {"_id": _to_oid(review_id)},
        {"$set": {"reply": reply, "updated_at": now}},
        return_document=ReturnDocument.AFTER,
    )
    return doc



async def recompute_business_rating(db: AsyncIOMotorDatabase, business_id: str) -> None:
    """
    Recalcula promedio y conteo de reseñas del negocio.
    Corrige el error 'a group specification must include an _id' usando _id: None.
    Acepta business_id guardado como str u ObjectId en la colección de reseñas.
    """
    ids = _id_choices(business_id)
    pipeline = [
        {"$match": {"business_id": {"$in": ids}, "rating": {"$gte": 1}}},
        {"$group": {"_id": None, "avg": {"$avg": "$rating"}, "count": {"$sum": 1}}},
    ]

    agg = await db[COLL].aggregate(pipeline).to_list(1)
    if agg:
        avg = float(agg[0].get("avg") or 0.0)
        count = int(agg[0].get("count") or 0)
    else:
        avg = 0.0
        count = 0


    avg_rounded = round(avg, 1)


    await db[BUSINESSES].update_one(
        {"_id": _to_oid(business_id)},
        {"$set": {"avg_rating": avg_rounded, "reviews_count": count, "rating": avg_rounded}},
    )
