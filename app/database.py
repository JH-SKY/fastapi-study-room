import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# 현재 파일(database.py)의 위치를 기준으로 상위 폴더(..)에 있는 .env 찾기
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
# .env 파일에서 DATABASE_URL 읽어오기
DATABASE_URL = os.getenv("DATABASE_URL")

# DB 엔진 생성
engine = create_engine(DATABASE_URL)

# 세션 생성기 정의
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy 2.0 스타일의 Base 클래스 선언
class Base(DeclarativeBase):
    pass

# DB 세션 의존성 주입 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

print(f"DEBUG: DATABASE_URL is -> {DATABASE_URL}")

if DATABASE_URL is None:
    print("❌ 에러: .env 파일을 찾지 못했거나 내용이 비어있습니다!")