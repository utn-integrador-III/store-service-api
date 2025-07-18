from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Appointment(BaseModel):
    id_cita: str = Field(alias="_id") 
    id_cliente: str
    id_servicio: str
    fecha_cita: datetime
    estado: str
    notas: Optional[str] = None
    fecha_creacion: datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

class CreateAppointmentSchema(BaseModel):
    id_cliente: str = Field(..., example="CLIENTE_001")
    id_servicio: str = Field(..., example="SER_003")
    fecha_cita: datetime = Field(..., example="2025-08-22T14:30:00")
    notas: Optional[str] = Field(None, example="Cliente alérgico al látex.")