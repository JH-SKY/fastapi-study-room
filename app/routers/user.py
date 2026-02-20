from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import user_service  # 변수(인스턴스)를 가져옴

router = APIRouter(prefix="/users", tags=["users"])

