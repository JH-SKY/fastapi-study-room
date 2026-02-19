from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from typing import List, TYPE_CHECKING

# 순환 참조 방지: 타입 검사 시에만 임포트
if TYPE_CHECKING:
    from app.models.reservation import Reservation
    from app.models.review import Review

class User(Base):
    __tablename__ = "users"

    # 기본키 및 사용자 정보
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(unique=True, index=True, nullable=False) # 학번 (Login ID)
    password: Mapped[str] = mapped_column(nullable=False) # 암호화 저장 예정
    name: Mapped[str] = mapped_column(nullable=False)

    # 관계 설정: User는 여러 Reservation/Review를 가질 수 있음
    reservations: Mapped[List["Reservation"]] = relationship("Reservation", back_populates="user")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="user")