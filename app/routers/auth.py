from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse
from app.services.auth_service import auth_service
from sqlalchemy.ext.asyncio import AsyncSession
HTTPException


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await auth_service.signup(db , data)

@router.post("/login", response_model=Token)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    return await auth_service.login(db, data)