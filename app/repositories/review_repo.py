from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.review import Review

class ReviewRepository:
    async def get_by_reservation_id(self, db: AsyncSession, res_id: int):
        result = await db.execute(select(Review).where(Review.reservation_id == res_id))
        return result.scalars().first()

    async def get_by_id(self, db: AsyncSession, review_id: int):
        result = await db.execute(select(Review).where(Review.id == review_id))
        return result.scalars().first()

    async def get_all_by_room(self, db: AsyncSession, room_id: int):
        result = await db.execute(select(Review).where(Review.room_id == room_id))
        return result.scalars().all()

    async def save(self, db: AsyncSession, review: Review):
        db.add(review)
        await db.flush()
        return review

    async def delete(self, db: AsyncSession, review: Review):
        await db.delete(review)

review_repo = ReviewRepository()