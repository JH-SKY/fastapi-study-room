from sqlalchemy import ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from datetime import date
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.room import StudyRoom
    from app.models.review import Review

class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    
    reservation_date: Mapped[date] = mapped_column(Date, nullable=False) # 예약 날짜
    start_time: Mapped[int] = mapped_column(nullable=False) # 시작 (예: 14)
    end_time: Mapped[int] = mapped_column(nullable=False) # 종료 (예: 16)
    status: Mapped[str] = mapped_column(default="CONFIRMED") # 상태 관리

    # 관계 설정: N:1 관계 및 Review와의 관계
    user: Mapped["User"] = relationship("User", back_populates="reservations")
    room: Mapped["StudyRoom"] = relationship("StudyRoom", back_populates="reservations")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="reservation")