from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator
from datetime import date, datetime, time
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

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def current_status(self) -> str:
        """DB 데이터와 현재 시간을 대조하여 실시간 상태를 계산"""
        if self.status == "CANCELLED":
            return "CANCELLED"
        
        now = datetime.now()
        # 서비스 레이어 로직과 동일하게 날짜와 시간을 결합
        res_start = datetime.combine(self.reservation_date, time(hour=self.start_time))
        res_end = datetime.combine(self.reservation_date, time(hour=self.end_time))

        if now < res_start:
            return "UPCOMING"    # 이용 대기
        elif res_start <= now < res_end:
            return "IN_USE"      # 이용 중
        else:
            return "COMPLETED"   # 이용 완료