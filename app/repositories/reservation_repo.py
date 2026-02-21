from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.reservation import Reservation

class ReservationRepository:
    async def find_overlap(self, db: AsyncSession, res_date, start, end, room_id=None, user_id=None, exclude_id=None):
        """[규칙 5, 7] 중복 체크: (기존_시작 < 새_종료) AND (기존_종료 > 새_시작)"""
        query = select(Reservation).where(
            and_(
                Reservation.reservation_date == res_date,
                Reservation.start_time < end,
                Reservation.end_time > start,
                Reservation.status != "CANCELLED"
            )
        )
        
        # 필터 조건 추가
        if room_id: 
            query = query.where(Reservation.room_id == room_id)
        if user_id: 
            query = query.where(Reservation.user_id == user_id)
        if exclude_id: 
            query = query.where(Reservation.id != exclude_id)
        
        result = await db.execute(query)
        # scalars().first()는 결과가 없으면 None을 반환하므로 서비스 레이어에서 조건문 처리에 최적입니다.
        return result.scalars().first()

    async def get_by_id(self, db: AsyncSession, res_id: int):
        """ID로 단건 조회 (수정/취소 시 검증용)"""
        result = await db.execute(select(Reservation).where(Reservation.id == res_id))
        return result.scalars().first()

    async def get_my_list(self, db: AsyncSession, user_id: int):
        """특정 유저의 전체 예약 목록 조회"""
        result = await db.execute(
            select(Reservation)
            .where(Reservation.user_id == user_id)
            .order_by(Reservation.reservation_date.desc(), Reservation.start_time.desc())
        )
        return result.scalars().all()

    async def save(self, db: AsyncSession, reservation: Reservation):
        """
        객체를 세션에 추가합니다. 
        실제 DB 반영(Commit)은 서비스 레이어에서 결정합니다.
        """
        db.add(reservation)
        # flush를 사용하면 commit 전에 DB 아이디(id) 등을 미리 할당받을 수 있어 유용합니다.
        await db.flush() 
        return reservation

reservation_repo = ReservationRepository()