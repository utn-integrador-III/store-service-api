from __future__ import annotations
from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, conint


class ReviewReply(BaseModel):
    text: str
    role: str = "owner"
    created_at: Optional[datetime] = None


class ReviewBase(BaseModel):

    business_id: Any
    appointment_id: Optional[Any] = None
    rating: conint(ge=1, le=5)
    comment: str = ""


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    rating: Optional[conint(ge=1, le=5)] = None
    comment: Optional[str] = None
    reply: Optional[ReviewReply] = None


class ReviewInDB(ReviewBase):
    id: Any = Field(alias="_id")
    user_id: Any
    created_at: datetime

    updated_at: Optional[datetime] = None
    reply: Optional[ReviewReply] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class ReviewResponse(ReviewInDB):
    """Modelo de salida."""
    pass
