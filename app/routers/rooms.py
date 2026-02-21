from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.room import RoomCreate, RoomResponse, RoomUpdate
from app.services.room_service import room_service
from app.services.auth_service import get_current_admin_user

router = APIRouter(prefix="/rooms", tags=["Rooms"])

# 방생성
# @router.post("/", response_model=RoomResponse)
# async def create_room(room_in: RoomCreate, db: AsyncSession = Depends(get_db)):
#     return await room_service.create_room(db, room_in)

# 방생성 (관리자 권한 필요)
@router.post("/", response_model=RoomResponse)
async def create_room(
    room_in: RoomCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user) 
):
    return await room_service.create_room(db, room_in)

@router.get("/", response_model=list[RoomResponse])
async def get_rooms(db: AsyncSession = Depends(get_db)):
    return await room_service.get_rooms(db)

@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(room_id: int, db: AsyncSession = Depends(get_db)):
    return await room_service.get_room(db, room_id)

# 방 정보 수정 (관리자 전용)
@router.patch("/{room_id}", response_model=RoomResponse)
async def update_room(
    room_id: int,
    room_in: RoomUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user) # 👈 관리자 체크!
):
    """
    특정 방의 정보를 수정합니다. (관리자 권한 필요)
    수정하고 싶은 필드만 담아서 보내면 해당 부분만 업데이트됩니다.
    """
    return await room_service.update_room(db, room_id, room_in)

# 방 삭제 (관리자 전용)
@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user) # 👈 관리자 체크!
):
    """
    특정 방을 삭제합니다. (관리자 권한 필요)
    성공 시 데이터 없이 204 No Content를 반환합니다.
    """
    await room_service.delete_room(db, room_id)
    return None