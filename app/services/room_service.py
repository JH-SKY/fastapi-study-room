from http.client import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.room import StudyRoom
from app.schemas.room import RoomCreate, RoomUpdate
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
    
    # 전체조회
    async def get_rooms(self, db: AsyncSession):
        # 레포지토리의 get_rooms를 호출해서 결과만 바로 반환
        return await room_repo.get_all_rooms(db)
    
    # 단일조회
    async def get_room(self, db: AsyncSession, room_id: int):
        room = await room_repo.get_room_by_id(db, room_id)
        if not room:
            # 데이터가 없을 때 404 에러를 던지는 건 실무 필수 매너!
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="해당 방을 찾을 수 없습니다.")
        return room
    
    # 업데이트
    async def update_room(self, db: AsyncSession, room_id: int, room_in: RoomUpdate):
            async with db.begin(): # 👈 트랜잭션 관리(관리자)
                # 1. 조회
                room = await room_repo.get_room_by_id(db, room_id)
                if not room:
                    raise HTTPException(status_code=404, detail="방을 찾을 수 없습니다.")

                # 2. 업데이트 데이터 준비
                update_data = room_in.model_dump(exclude_unset=True)

                # 3. 실제 업데이트 "행위"는 레포에게 시킴
                updated_room = await room_repo.update_room(db, room, update_data)
            
            # with 종료 후 자동 commit
            await db.refresh(updated_room)
            return updated_room

    # 삭제
    async def delete_room(self, db: AsyncSession, room_id: int):
        async with db.begin():
            # 1. 대상 조회
            room = await room_repo.get_room_by_id(db, room_id)
            if not room:
                raise HTTPException(status_code=404, detail="방을 찾을 수 없습니다.")

            
            await room_repo.delete_room(db, room)

room_service = RoomService()