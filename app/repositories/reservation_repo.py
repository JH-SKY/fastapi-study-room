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
        if room_id: query = query.where(Reservation.room_id == room_id)
        if user_id: query = query.where(Reservation.user_id == user_id)
        if exclude_id: query = query.where(Reservation.id != exclude_id)
        
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_id(self, db: AsyncSession, res_id: int):
        result = await db.execute(select(Reservation).where(Reservation.id == res_id))
        return result.scalars().first()

    async def get_my_list(self, db: AsyncSession, user_id: int):
        result = await db.execute(select(Reservation).where(Reservation.user_id == user_id))
        return result.scalars().all()

    async def save(self, db: AsyncSession, reservation: Reservation):
        db.add(reservation)
        return reservation

reservation_repo = ReservationRepository()