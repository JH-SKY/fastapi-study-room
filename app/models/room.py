from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.reservation import Reservation
    from app.models.review import Review

class StudyRoom(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False) # 방 이름
    floor: Mapped[int] = mapped_column(nullable=False) # 층수
    capacity: Mapped[int] = mapped_column(nullable=False) # 수용 인원
    has_whiteboard: Mapped[bool] = mapped_column(default=False)
    has_projector: Mapped[bool] = mapped_column(default=False)

    # 관계 설정: Room은 여러 Reservation/Review와 연결됨
    reservations: Mapped[List["Reservation"]] = relationship("Reservation", back_populates="room")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="room")