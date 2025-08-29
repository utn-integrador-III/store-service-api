from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

def _oid(id_str: str) -> ObjectId:
    return ObjectId(id_str)

async def get_employees_by_business(db: AsyncIOMotorDatabase, business_id: str, include_inactive: bool = False) -> List[Dict[str, Any]]:
    q: Dict[str, Any] = {"business_id": _oid(business_id)}
    if not include_inactive:
        q["active"] = True
    return await db["employees"].find(q).to_list(length=None)

async def create_employee(db: AsyncIOMotorDatabase, business_id: str, name: str, active: bool = True) -> Dict[str, Any]:
    doc = {"business_id": _oid(business_id), "name": name, "active": active, "allowed_slots": {}}
    res = await db["employees"].insert_one(doc)
    return await db["employees"].find_one({"_id": res.inserted_id})

async def update_employee(db: AsyncIOMotorDatabase, employee_id: str, update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    await db["employees"].update_one({"_id": _oid(employee_id)}, {"$set": update})
    return await db["employees"].find_one({"_id": _oid(employee_id)})

async def delete_employee(db: AsyncIOMotorDatabase, employee_id: str) -> None:
    await db["employees"].delete_one({"_id": _oid(employee_id)})

async def set_allowed_slots(db: AsyncIOMotorDatabase, employee_id: str, allowed_slots: Dict[str, List[str]]) -> Optional[Dict[str, Any]]:
    await db["employees"].update_one({"_id": _oid(employee_id)}, {"$set": {"allowed_slots": allowed_slots}})
    return await db["employees"].find_one({"_id": _oid(employee_id)})

async def get_employee(db: AsyncIOMotorDatabase, employee_id: str) -> Optional[Dict[str, Any]]:
    return await db["employees"].find_one({"_id": _oid(employee_id)})
