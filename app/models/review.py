import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.room import StudyRoom
    from app.models.reservation import Reservation

# 리뷰 모델(중계테이블)
class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    reservation_id: Mapped[int] = mapped_column(ForeignKey("reservations.id"), nullable=False)
    
    rating: Mapped[int] = mapped_column(nullable=False) # 1~5점
    content: Mapped[str] = mapped_column(nullable=True) # 리뷰 내용
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # 관계 설정: 모든 외래키 대상과 연결
    user: Mapped["User"] = relationship("User", back_populates="reviews")
    room: Mapped["StudyRoom"] = relationship("StudyRoom", back_populates="reviews")
    reservation: Mapped["Reservation"] = relationship("Reservation", back_populates="reviews")
    