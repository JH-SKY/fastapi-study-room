from sqlalchemy.orm import Session, AsyncSession
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate  # Pydantic 모델
from app.repositories.user_repo import user_repo  # 사용자 레포지토리 임포트
from app.services.auth_service import pwd_context

class UserService():
    async def update_user(self, db: AsyncSession, user: User, user_in: UserUpdate):
        update_data = user_in.model_dump(exclude_unset=True)
        
        # 비즈니스 로직: 비밀번호가 있으면 해싱 처리
        if "password" in update_data:
            update_data["password"] = pwd_context.hash(update_data["password"])
        
        # 실제 DB 수정 작업은 레포지토리에게 위임!
        updated_user = await user_repo.update(db, user, update_data)
        
        await db.commit() # 오늘 배운 트랜잭션 마무리
        await db.refresh(updated_user)
        return updated_user




user_service = UserService()