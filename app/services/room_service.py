from sqlalchemy.ext.asyncio import AsyncSession
from app.models.room import StudyRoom
from app.schemas.room import RoomCreate
from app.repositories.room_repo import room_repo


class RoomService:
    async def create_room(self,db: AsyncSession, room_in: RoomCreate):
        new_room = StudyRoom(**room_in.model_dump())
                # 2. 레포지토리에 맡기기 (이 안에서 db.add와 flush가 일어남)
        await room_repo.save_room(db, new_room)
            
            # 3. 트랜잭션 종료 후 데이터 최신화
        try:
            await db.commit() 
            await db.refresh(new_room)
        except Exception as e:
            await db.rollback()
            raise e
                
        return new_room
    
    async def get_rooms(self, db: AsyncSession):
        # 레포지토리의 get_rooms를 호출해서 결과만 바로 반환
        return await room_repo.get_all_rooms(db)

room_service = RoomService()