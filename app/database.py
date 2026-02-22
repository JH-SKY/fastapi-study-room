import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# 현재 파일(database.py)의 위치를 기준으로 상위 폴더(..)에 있는 .env 찾기
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
# .env 파일에서 DATABASE_URL 읽어오기
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

# DB 엔진 생성
engine = create_async_engine(DATABASE_URL, echo=True)

# 세션 생성기 정의
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# SQLAlchemy 2.0 스타일의 Base 클래스 선언
class Base(DeclarativeBase):
    pass
 
# DB 세션 의존성 주입 함수
async def get_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            # async with를 쓰면 자동으로 닫히지만, 
            # 명시적으로 await db.close()를 넣기도 합니다.
            await db.close()