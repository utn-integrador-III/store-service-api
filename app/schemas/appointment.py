
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Any
from bson import ObjectId
from .utils import PyObjectId

class AppointmentCreate(BaseModel):
    business_id: str
    appointment_time: datetime

class AppointmentResponse(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    business_id: str 
    appointment_time: datetime

    @field_validator("id", "user_id", "business_id", mode='before') 
    @classmethod
    def convert_objectid_to_str(cls, v: Any) -> str:
        if isinstance(v, ObjectId):
            return str(v)
        return v
    
    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}