from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List

from app.db.session import get_database
from app.schemas.user import UserResponse
from app.schemas.appointment import AppointmentCreate, AppointmentResponse
from app.crud import crud_appointment
from app.core.security import get_current_user

router = APIRouter()

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment_in: AppointmentCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Crea una nueva cita.
    """
    appointment = await crud_appointment.create(
        db=db,
        business_id=appointment_in.business_id,
        user_id=current_user.id,
        appointment_time=appointment_in.appointment_time
    )
    
    return AppointmentResponse.model_validate(appointment)

@router.get("/me", response_model=List[AppointmentResponse])
async def get_my_appointments(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    appointments = await crud_appointment.get_appointments_by_user_id(db, user_id=current_user.id)
    return [AppointmentResponse.model_validate(app) for app in appointments]


@router.get("/business/{business_id}", response_model=List[AppointmentResponse])
async def get_business_appointments(
    business_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    appointments = await crud_appointment.get_appointments_by_business_id(db, business_id=business_id)
    return [AppointmentResponse.model_validate(app) for app in appointments]