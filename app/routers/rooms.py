from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.room import RoomCreate, RoomResponse
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
    current_user: User = Depends(get_current_admin_user) # <- 이 자물쇠가 빠졌습니다!
):
    return await room_service.create_room(db, room_in)

@router.get("/", response_model=list[RoomResponse])
async def get_rooms(db: AsyncSession = Depends(get_db)):
    return await room_service.get_rooms(db)