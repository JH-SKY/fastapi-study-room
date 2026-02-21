from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import get_current_user
from app.services.user_service import user_service  # 변수(인스턴스)를 가져옴

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
async def get_my_info(current_user: User = Depends(get_current_user)):
    """
    [내 정보 조회]
    - 헤더의 토큰을 통해 현재 로그인한 유저의 전체 정보를 반환합니다.
    """
    return current_user