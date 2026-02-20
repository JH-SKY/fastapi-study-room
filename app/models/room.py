from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.reservation import Reservation
    from app.models.review import Review

# 스터디룸 모델
class StudyRoom(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False) # 방 이름
    floor: Mapped[int] = mapped_column(nullable=False) # 층수
    capacity: Mapped[int] = mapped_column(nullable=False) # 수용 인원
    has_whiteboard: Mapped[bool] = mapped_column(default=False)
    has_projector: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    image_url: Mapped[str| None] = mapped_column(nullable=True)
    # [v1.3 추가] 방의 상세 설명 (예: 화이트보드 유무, 채광 등)
    description: Mapped[str | None] = mapped_column(nullable=True)

    # 관계 설정: Room은 여러 Reservation/Review와 연결됨
    reservations: Mapped[List["Reservation"]] = relationship("Reservation", back_populates="room")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="room")