from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ReviewCreate(BaseModel):
    reservation_id: int
    rating: int = Field(..., ge=1, le=5, description="1점부터 5점까지 입력 가능합니다.")
    content: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    user_id: int
    room_id: int
    reservation_id: int
    rating: int
    content: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True