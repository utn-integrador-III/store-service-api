
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from .utils import PyObjectId
from bson import ObjectId

class OwnerRequestSchema(BaseModel):
    business_name: str
    business_description: str
    address: str  
    logo_url: Optional[str] = None 
    status: str = 'pending'

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    role: str = 'usuario'
    owner_request: Optional[OwnerRequestSchema] = None
    profile_picture_url: Optional[str] = None 
    
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    profile_picture_url: Optional[str] = None 

class UserResponse(UserBase):
    id: PyObjectId = Field(alias="_id")
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None