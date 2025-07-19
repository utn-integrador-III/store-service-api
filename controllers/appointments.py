from fastapi import APIRouter, HTTPException, Body, status
from bd.mono_client import Connection
from models.appointments import CreateAppointmentSchema, Appointment
from datetime import datetime

router = APIRouter()
appointments_db = Connection(collection_name="Appointments")

@router.post(
    "/citas/",
    response_model=Appointment,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva cita",
    tags=["Citas"]
)
def create_appointment(appointments: CreateAppointmentSchema = Body(...)):
    """
    Registra una nueva cita en el sistema.
    """
    try:
        appointment_data = appointments.model_dump()
        appointment_data["estado"] = "agendada"
        appointment_data["fecha_creacion"] = datetime.now()

        new_appointment = appointments_db.create_data(appointment_data)
        
        if not new_appointment:
             raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="La operación de creación no devolvió el nuevo documento."
            )

        return new_appointment
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Ha ocurrido un error inesperado en el controlador: {e}"
        )