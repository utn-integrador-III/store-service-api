
from pydantic import BaseModel, Field, field_validator
from bson import ObjectId
from typing import Any
from .user import PyObjectId 

class ServiceBase(BaseModel):
    name: str
    category: str
    location: str
    image_url: str | None = None

class ServiceInDB(ServiceBase):
    id: PyObjectId = Field(alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ServiceResponse(ServiceBase):
    id: str = Field(..., alias="_id")

    @field_validator("id", mode='before')
    @classmethod
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}