from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Dict, Any, Optional

from app.db.session import get_database

router = APIRouter()

def _oid(id_str: str) -> ObjectId:
    if not ObjectId.is_valid(id_str):
        raise HTTPException(status_code=400, detail="ID inválido")
    return ObjectId(id_str)

def _employee_to_response(doc: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(doc.get("_id")),
        "business_id": str(doc.get("business_id")) if isinstance(doc.get("business_id"), ObjectId) else doc.get("business_id"),
        "name": doc.get("name", ""),
        "active": bool(doc.get("active", True)),
        "allowed_slots": doc.get("allowed_slots", {}),  
    }

@router.get("/businesses/{business_id}/employees")
async def list_employees(
    business_id: str,
    include_inactive: bool = Query(False),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> List[Dict[str, Any]]:
    q: Dict[str, Any] = {"business_id": _oid(business_id)}
    if not include_inactive:
        q["active"] = True
    cur = db["employees"].find(q)
    items = await cur.to_list(length=None)
    return [_employee_to_response(x) for x in items]

@router.post("/businesses/{business_id}/employees", status_code=status.HTTP_201_CREATED)
async def create_employee(
    business_id: str,
    payload: Dict[str, Any],
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Dict[str, Any]:
    name = (payload.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Nombre requerido")
    doc = {
        "business_id": _oid(business_id),
        "name": name,
        "active": bool(payload.get("active", True)),
        "allowed_slots": {},
    }
    res = await db["employees"].insert_one(doc)
    created = await db["employees"].find_one({"_id": res.inserted_id})
    return _employee_to_response(created)

@router.patch("/employees/{employee_id}")
async def update_employee(
    employee_id: str,
    payload: Dict[str, Any],
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Dict[str, Any]:
    update: Dict[str, Any] = {}
    if "name" in payload:
        update["name"] = (payload["name"] or "").strip()
    if "active" in payload:
        update["active"] = bool(payload["active"])
    if not update:
        raise HTTPException(status_code=400, detail="Nada para actualizar")
    await db["employees"].update_one({"_id": _oid(employee_id)}, {"$set": update})
    doc = await db["employees"].find_one({"_id": _oid(employee_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return _employee_to_response(doc)

@router.delete("/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(employee_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    await db["employees"].delete_one({"_id": _oid(employee_id)})
    return {}

@router.put("/employees/{employee_id}/allowed-slots")
async def set_allowed_slots(
    employee_id: str,
    payload: Dict[str, Any],
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Dict[str, Any]:
    allowed_slots = payload.get("allowed_slots") or {}
    if not isinstance(allowed_slots, dict):
        raise HTTPException(status_code=400, detail="allowed_slots debe ser un objeto")
    norm: Dict[str, List[str]] = {}
    for k, v in allowed_slots.items():
        if isinstance(v, list):
            norm[k] = [str(x) for x in v]
    await db["employees"].update_one({"_id": _oid(employee_id)}, {"$set": {"allowed_slots": norm}})
    doc = await db["employees"].find_one({"_id": _oid(employee_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return _employee_to_response(doc)

@router.get("/employees/{employee_id}")
async def get_employee(employee_id: str, db: AsyncIOMotorDatabase = Depends(get_database)) -> Dict[str, Any]:
    doc = await db["employees"].find_one({"_id": _oid(employee_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return _employee_to_response(doc)
