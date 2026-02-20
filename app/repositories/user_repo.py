from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select  # 2.0 버전의 핵심!
from app.models.user import User
from app.schemas.user import UserCreate

class UserRepository:
    async def get_by_student_id(self, db: AsyncSession, student_id: str):
        # 2.0 비동기 방식: select 문을 만들고 db.execute로 실행합니다.
        query = select(User).where(User.student_id == student_id)
        result = await db.execute(query)
        
        # scalars().first()는 결과물 중 첫 번째 객체(User)만 쏙 뽑아오는 기능
        return result.scalars().first()

    # 2. 사용자 생성 로직 
    async def create(self, db: AsyncSession, user_in: UserCreate, hashed_password: str):
        db_user = User(
            student_id=user_in.student_id,
            name=user_in.name,
            password=hashed_password
        )
        db.add(db_user)
        # 3. flush도 비동기 작업이므로 await를 붙입니다.
        # flush는 DB에 "일단 이 데이터 넣을 준비해!"
        await db.flush() 
        return db_user

user_repo = UserRepository()