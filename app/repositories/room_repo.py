from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.room import StudyRoom

class RoomRepository:
    async def save_room(self, db: AsyncSession, room_obj: StudyRoom):
        db.add(room_obj)
        # 여기서 flush를 해주면 DB에 ID가 임시로 생성되어 반환 시 ID 확인이 가능합니다.
        await db.flush()
        return room_obj

    # 전체 조회: 모든 스터디룸 목록 가져오기
    async def get_all_rooms(self,db: AsyncSession):
        result = await db.execute(select(StudyRoom))
        return result.scalars().all()

    # 단일 조회: ID로 특정 방 찾기 (수정/삭제 시 필수)
    async def get_room_by_id(self,db: AsyncSession, room_id: int):
        result = await db.execute(select(StudyRoom).where(StudyRoom.id == room_id))
        return result.scalar_one_or_none()
    

room_repo = RoomRepository()