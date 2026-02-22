from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.room import StudyRoom
from app.schemas.room import RoomCreate, RoomUpdate
from app.repositories.room_repo import room_repo
from app.repositories.reservation_repo import reservation_repo # 👈 추가: 예약 확인용

class RoomService:
    async def create_room(self, db: AsyncSession, room_in: RoomCreate):
        new_room = StudyRoom(**room_in.model_dump())
        await room_repo.save_room(db, new_room)
        
        try:
            await db.commit() 
            await db.refresh(new_room)
        except Exception as e:
            await db.rollback()
            raise e
                
        return new_room
    
    # [수정] 전체 조회: 실시간 상태(availability_status) 계산 로직 추가
    async def get_rooms(self, db: AsyncSession):
        rooms = await room_repo.get_all_rooms(db)
        now = datetime.now()

        for room in rooms:
            # 1. 운영 여부 확인
            if not room.is_active:
                room.availability_status = "INACTIVE"
                continue
            
            # 2. 현재 시간 중복 예약 확인 (Repo의 find_overlap 활용)
            # 현재 시간을 시작점으로 1시간 동안 예약이 있는지 확인
            is_reserved = await reservation_repo.find_overlap(
                db, 
                res_date=now.date(), 
                start=now.hour, 
                end=now.hour + 1, 
                room_id=room.id
            )

            # 3. 계산된 상태 주입
            room.availability_status = "IN_USE" if is_reserved else "AVAILABLE"
            
        return rooms
    
    # [수정] 단일 조회: 실시간 상태 계산 로직 추가
    async def get_room(self, db: AsyncSession, room_id: int):
        room = await room_repo.get_room_by_id(db, room_id)
        if not room:
            raise HTTPException(status_code=404, detail="해당 방을 찾을 수 없습니다.")
        
        # 실시간 상태 계산
        now = datetime.now()
        if not room.is_active:
            room.availability_status = "INACTIVE"
        else:
            is_reserved = await reservation_repo.find_overlap(
                db, now.date(), now.hour, now.hour + 1, room_id=room.id
            )
            room.availability_status = "IN_USE" if is_reserved else "AVAILABLE"
            
        return room
    
    async def update_room(self, db: AsyncSession, room_id: int, room_in: RoomUpdate):
        # async with db.begin()을 쓰면 내부에서 commit/rollback을 알아서 관리합니다.
        async with db.begin():
            room = await room_repo.get_room_by_id(db, room_id)
            if not room:
                raise HTTPException(status_code=404, detail="방을 찾을 수 없습니다.")

            update_data = room_in.model_dump(exclude_unset=True)
            updated_room = await room_repo.update_room(db, room, update_data)
        
        await db.refresh(updated_room)
        return updated_room

    async def delete_room(self, db: AsyncSession, room_id: int):
        async with db.begin():
            room = await room_repo.get_room_by_id(db, room_id)
            if not room:
                raise HTTPException(status_code=404, detail="방을 찾을 수 없습니다.")
            
            await room_repo.delete_room(db, room)

    

room_service = RoomService()