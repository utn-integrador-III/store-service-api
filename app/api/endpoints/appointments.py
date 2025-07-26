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