from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.review import Review
from app.repositories import review_repo
from app.schemas.review import ReviewCreate, ReviewResponse
from app.services.review_service import review_service
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=ReviewResponse)
async def create_review(
    review_in: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await review_service.create_review(db, current_user.id, review_in)

@router.delete("/{review_id}")
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await review_service.delete_review(db, current_user.id, review_id)

@router.get("/room/{room_id}", response_model=list[ReviewResponse])
async def get_room_reviews(
    room_id: int,
    db: AsyncSession = Depends(get_db)
):
    """특정 스터디룸의 모든 리뷰 조회 (로그인 불필요)"""
    return await review_repo.get_all_by_room(db, room_id)

@router.get("/me", response_model=list[ReviewResponse])
async def get_my_reviews(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """내가 작성한 리뷰 목록 조회"""
    # 레포지토리에 get_all_by_user 함수를 추가하거나 여기서 직접 쿼리
    result = await db.execute(select(Review).where(Review.user_id == current_user.id))
    return result.scalars().all()