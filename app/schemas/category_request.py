
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal, Any
from .user import PyObjectId
from bson import ObjectId
from datetime import datetime

class CategoryRequestBase(BaseModel):
    category_name: str = Field(..., max_length=50)
    reason: str = Field(..., max_length=500)
    evidence_url: Optional[str] = None

class CategoryRequestCreate(CategoryRequestBase):
    pass 

class CategoryRequestInDB(CategoryRequestBase):
    id: PyObjectId = Field(alias="_id")
    owner_id: PyObjectId
    status: Literal["pending", "approved", "rejected"] = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class CategoryRequestResponse(CategoryRequestBase):
    id: str = Field(..., alias="_id")
    owner_id: str
    status: str
    created_at: datetime

    @field_validator("id", "owner_id", mode='before')
    @classmethod
    def convert_objectid_to_str(cls, v: Any) -> str:
        if isinstance(v, ObjectId):
            return str(v)
        return v
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}