from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any
from bson import ObjectId

class EmployeeScheduleDay(BaseModel):
    is_active: bool = False
    open_time: str = "09:00"            
    close_time: str = "17:00"
    slot_duration_minutes: int = 30
    capacity_per_slot: int = 1

class EmployeeSchedule(BaseModel):
    monday: EmployeeScheduleDay = EmployeeScheduleDay()
    tuesday: EmployeeScheduleDay = EmployeeScheduleDay()
    wednesday: EmployeeScheduleDay = EmployeeScheduleDay()
    thursday: EmployeeScheduleDay = EmployeeScheduleDay()
    friday: EmployeeScheduleDay = EmployeeScheduleDay()
    saturday: EmployeeScheduleDay = EmployeeScheduleDay()
    sunday: EmployeeScheduleDay = EmployeeScheduleDay()

class EmployeeBase(BaseModel):
    name: str
    active: bool = True
    roles: Optional[List[str]] = None

class EmployeeCreate(EmployeeBase):
    business_id: str

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    active: Optional[bool] = None
    roles: Optional[List[str]] = None

class EmployeeScheduleUpdate(EmployeeSchedule):
    pass

class EmployeeResponse(BaseModel):
    id: str = Field(..., alias="_id")
    business_id: str
    name: str
    active: bool = True
    roles: List[str] = []
    schedule: Optional[EmployeeSchedule] = None

    @field_validator("id", "business_id", mode="before")
    @classmethod
    def _oid_to_str(cls, v: Any) -> str:
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True
