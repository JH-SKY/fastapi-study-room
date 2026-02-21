from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from typing import Optional, List

class ReservationBase(BaseModel):
    room_id: int
    reservation_date: date
    start_time: int = Field(..., ge=9, le=21, description="9시~21시 시작 가능")
    end_time: int = Field(..., ge=10, le=22, description="10시~22시 종료 가능")

class ReservationCreate(ReservationBase):
    @field_validator("end_time")
    @classmethod
    def validate_duration(cls, v, info):
        start = info.data.get("start_time")
        if start is not None:
            duration = v - start
            # [규칙 1] 최소 1시간 단위 (int이므로 정수 체크)
            if duration < 1:
                raise ValueError("최소 예약 시간은 1시간입니다.")
            # [규칙 2] 최대 2시간 제한
            if duration > 2:
                raise ValueError("최대 예약 가능 시간은 2시간입니다.")
        return v

class ReservationUpdate(BaseModel):
    start_time: Optional[int] = Field(None, ge=9, le=21)
    end_time: Optional[int] = Field(None, ge=10, le=22)

class ReservationResponse(ReservationBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    canceled_at: Optional[datetime] = None

    class Config:
        from_attributes = True