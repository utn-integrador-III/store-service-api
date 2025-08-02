from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.db.session import get_database
from app.crud import crud_business
from app.schemas.business import BusinessCreate, BusinessUpdate, BusinessResponse, Schedule
from app.schemas.user import UserResponse
from app.core.security import get_current_user

router = APIRouter()

def convert_business_to_response(business: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(business["_id"]),
        "owner_id": str(business["owner_id"]),
        "name": business.get("name"),
        "description": business.get("description"),
        "address": business.get("address"),
        "logo_url": business.get("logo_url"),
        "photos": business.get("photos", []),
        "categories": business.get("categories", []),
        "status": business.get("status"),
        "schedule": business.get("schedule")
    }

@router.get("/", response_model=List[BusinessResponse])
async def get_all_published_businesses(db: AsyncIOMotorDatabase = Depends(get_database)):
    businesses_from_db = await crud_business.get_published_businesses(db)
    return [convert_business_to_response(b) for b in businesses_from_db]


@router.get("/my-businesses", response_model=List[BusinessResponse])
async def get_my_businesses(db: AsyncIOMotorDatabase = Depends(get_database), current_user: UserResponse = Depends(get_current_user)):
    businesses = await crud_business.get_businesses_by_owner(db, str(current_user.id))
    return [convert_business_to_response(b) for b in businesses]

@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business_by_id(business_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    if not ObjectId.is_valid(business_id):
        raise HTTPException(status_code=400, detail="ID de negocio inválido")
    business = await crud_business.get_business(db, business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    return convert_business_to_response(business)


@router.post("/my-business/", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
async def create_my_business(business_in: BusinessCreate, db: AsyncIOMotorDatabase = Depends(get_database), current_user: UserResponse = Depends(get_current_user)):
    owner_id = str(current_user.id)
    business = await crud_business.create_business(db, business_in, owner_id)
    return convert_business_to_response(business)

@router.put("/my-business/{business_id}", response_model=BusinessResponse)
async def update_my_business(business_id: str, business_in: BusinessUpdate, db: AsyncIOMotorDatabase = Depends(get_database), current_user: UserResponse = Depends(get_current_user)):
    if not ObjectId.is_valid(business_id):
        raise HTTPException(status_code=400, detail="ID de negocio inválido")
    existing_business = await crud_business.get_business(db, business_id)
    if not existing_business or str(existing_business['owner_id']) != str(current_user.id):
        raise HTTPException(status_code=403, detail="No tienes permiso para editar este negocio")
    updated_business = await crud_business.update_business(db, business_id, business_in)
    if not updated_business:
        raise HTTPException(status_code=404, detail="No se pudo actualizar el negocio")
    return convert_business_to_response(updated_business)

@router.post("/my-business/{business_id}/publish", response_model=BusinessResponse)
async def publish_my_business(business_id: str, db: AsyncIOMotorDatabase = Depends(get_database), current_user: UserResponse = Depends(get_current_user)):
    business = await crud_business.get_business(db, business_id)
    if not business or str(business['owner_id']) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Acción no permitida")
    published_business = await crud_business.update_business_status(db, business_id, "published")
    if not published_business:
        raise HTTPException(status_code=404, detail="No se pudo publicar el negocio")
    return convert_business_to_response(published_business)

@router.put("/my-business/{business_id}/schedule", response_model=BusinessResponse)
async def manage_my_business_schedule(business_id: str, schedule_in: Schedule, db: AsyncIOMotorDatabase = Depends(get_database), current_user: UserResponse = Depends(get_current_user)):
    business = await crud_business.get_business(db, business_id)
    if not business or str(business['owner_id']) != str(current_user.id):
        raise HTTPException(status_code=403, detail="No tienes permiso para editar este horario")
    updated_business = await crud_business.update_business_schedule(db, business_id, schedule_in)
    return convert_business_to_response(updated_business)

@router.get("/{business_id}/available-slots", response_model=List[str])
async def get_available_slots(business_id: str, date: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    try:
        slots = await crud_business.get_available_slots_for_day(db, business_id, date)
        return slots
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/admin/assign-business", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
async def assign_business_to_owner(owner_id: str, business_in: BusinessCreate, db: AsyncIOMotorDatabase = Depends(get_database), current_user: UserResponse = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acción reservada para administradores")
    business = await crud_business.create_business(db, business_in, owner_id)
    return convert_business_to_response(business)