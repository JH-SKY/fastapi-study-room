import traceback
from app.database import AsyncSessionLocal
from fastapi import FastAPI, Request
from app.database import Base, engine
from app import models
from app.routers import auth, user
from app.services.auth_service import auth_service

# 기존 테이블 지우기
# models.Base.metadata.drop_all(bind=engine)

# 정의된 모델들을 기반으로 DB에 테이블을 생성한다.
# models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(user.router)
app.include_router(auth.router)

# 1. 테이블 생성 방식을 비동기(startup)로 변경
@app.on_event("startup")
async def startup():
    # 비동기 엔진을 사용하여 테이블 생성
    async with engine.begin() as conn:
        # run_sync를 쓰는 이유: metadata.create_all은 내부적으로 동기 함수라서 
        # 비동기 연결(conn) 내에서 실행시키기 위한 특수 도구입니다.
        await conn.run_sync(models.Base.metadata.create_all)

# @app.on_event("startup")
# async def startup():
#     # 1. 테이블 생성 (기존 로직)
#     async with engine.begin() as conn:
#         await conn.run_sync(models.Base.metadata.create_all)
    
#     # 2. 관리자 생성 로직 실행
#     async with AsyncSessionLocal() as db:
#         await auth_service.create_initial_admin(db)