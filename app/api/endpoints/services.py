
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from datetime import datetime, time, timedelta

from app.db.session import get_database
from app.schemas.user import UserResponse
from app.schemas.business import BusinessBase, BusinessCreate, BusinessResponse, BusinessUpdate, Schedule
from app.crud import crud_business, crud_user, crud_appointment
from app.core.security import get_current_user
from .users import get_current_admin_user

router = APIRouter()

@router.get("/")
async def get_all_published_businesses(db: AsyncIOMotorDatabase = Depends(get_database)):
    businesses_from_db = await crud_business.get_published_businesses(db)
    response_data = []
    for business in businesses_from_db:
        response_data.append({
            "id": str(business["_id"]),
            "owner_id": str(business["owner_id"]),
            "name": business.get("name", "Sin Nombre"),
            "description": business.get("description", ""),
            "address": business.get("address", "Sin Dirección"),
            "photos": business.get("photos", []),
            "categories": business.get("categories", []),
            "status": business.get("status", "draft"),
            "schedule": business.get("schedule")
        })
    return JSONResponse(content=response_data)


async def get_current_owner_user(current_user: UserResponse = Depends(get_current_user)):
    if current_user.role not in ["dueño", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acción solo para dueños o administradores")
    return current_user


@router.get("/my-businesses", response_model=List[BusinessResponse])
async def get_my_businesses(
    db: AsyncIOMotorDatabase = Depends(get_database),
    owner: UserResponse = Depends(get_current_owner_user)
):
    businesses = await crud_business.get_businesses_by_owner_id(db, owner.id)
    return [BusinessResponse.model_validate(b) for b in businesses]

@router.post("/my-business", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
async def register_new_business(
    business_in: BusinessCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    owner: UserResponse = Depends(get_current_owner_user)
):
    business_dict = business_in.model_dump()
    new_business = await crud_business.create_business(db, business_data=business_dict, owner_id=owner.id)
    return BusinessResponse.model_validate(new_business)

@router.put("/my-business/{business_id}", response_model=BusinessResponse)
async def update_my_business(
    business_id: str,
    business_in: BusinessUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    owner: UserResponse = Depends(get_current_owner_user)
):
    business = await crud_business.get_business_by_id(db, business_id)
    if not business or str(business['owner_id']) != owner.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para editar este negocio.")
    updated_business = await crud_business.update_business(db, business_id, owner.id, business_in)
    return BusinessResponse.model_validate(updated_business)

@router.put("/my-business/{business_id}/schedule", response_model=BusinessResponse)
async def update_schedule_for_business(
    business_id: str,
    schedule_in: Schedule,
    db: AsyncIOMotorDatabase = Depends(get_database),
    owner: UserResponse = Depends(get_current_owner_user)
):
    business = await crud_business.get_business_by_id(db, business_id)
    if not business or str(business['owner_id']) != owner.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para editar este horario.")
    updated_business = await crud_business.update_business_schedule(db, business_id, schedule_in)
    return BusinessResponse.model_validate(updated_business)

@router.post("/my-business/{business_id}/publish", response_model=BusinessResponse)
async def publish_my_business(
    business_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    owner: UserResponse = Depends(get_current_owner_user)
):
    business = await crud_business.get_business_by_id(db, business_id)
    if not business or str(business['owner_id']) != owner.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para publicar este negocio.")
    published = await crud_business.publish_business(db, business_id, owner.id)
    if not published:
        raise HTTPException(status_code=404, detail="El negocio no pudo ser publicado.")
    return BusinessResponse.model_validate(published)

@router.get("/{business_id}/available-slots")
async def get_available_slots(
    business_id: str,
    date: str, 
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    try:
        business = await crud_business.get_business_by_id(db, business_id)
        if not business or not business.get("schedule"):
            return []

        selected_date = datetime.strptime(date, "%Y-%m-%d")
        days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        day_name = days_of_week[selected_date.weekday()]
        schedule_day = business["schedule"].get(day_name)

        if not schedule_day or not schedule_day.get("is_active"):
            return []

        open_time_str = schedule_day.get("open_time")
        close_time_str = schedule_day.get("close_time")
        slot_duration = schedule_day.get("slot_duration_minutes")
        capacity = schedule_day.get("capacity_per_slot")

        if not all([open_time_str, close_time_str, slot_duration, capacity]):
            return []
        
        slot_duration = int(slot_duration)
        capacity = int(capacity)
        if slot_duration <= 0: return []

        open_time = datetime.strptime(open_time_str, "%H:%M").time()
        close_time = datetime.strptime(close_time_str, "%H:%M").time()

        all_slots = []
        current_time = datetime.combine(selected_date, open_time)
        end_time = datetime.combine(selected_date, close_time)

        while current_time < end_time:
            all_slots.append(current_time.strftime("%H:%M"))
            current_time += timedelta(minutes=slot_duration)

        existing_appointments = await crud_appointment.get_appointments_by_business_id_and_date(db, business_id, selected_date)
        
        slot_counts = {}
        for app in existing_appointments:
            slot_time = app["appointment_time"].strftime("%H:%M")
            slot_counts[slot_time] = slot_counts.get(slot_time, 0) + 1

        available_slots = [slot for slot in all_slots if slot_counts.get(slot, 0) < capacity]
            
        return available_slots

    except Exception as e:
     
        print(f"ERROR CRÍTICO al calcular horarios para {business_id} en {date}: {e}")
        return []


@router.get("/{business_id}", response_model=BusinessResponse)
async def get_single_business(business_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    business = await crud_business.get_business_by_id(db, business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    return BusinessResponse.model_validate(business)

@router.post("/admin/assign-business", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_and_assign_business(
    owner_id: str,
    business_in: BusinessCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    admin: UserResponse = Depends(get_current_admin_user)
):
    owner = await crud_user.get_user_by_id(db, owner_id)
    if not owner or owner['role'] != 'dueño':
        raise HTTPException(status_code=404, detail="El ID proporcionado no corresponde a un usuario con rol 'dueño'.")
    business_dict = business_in.model_dump()
    new_business = await crud_business.create_business(db, business_data=business_dict, owner_id=owner_id)
    return BusinessResponse.model_validate(new_business)