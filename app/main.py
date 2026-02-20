import traceback

from fastapi import FastAPI, Request
from app.database import Base, engine
from app import models
from app.routers import auth, user

# 기존 테이블 지우기
# models.Base.metadata.drop_all(bind=engine)

# 정의된 모델들을 기반으로 DB에 테이블을 생성한다.
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(user.router)
app.include_router(auth.router)


@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    return await call_next(request)
    # try:
    # except Exception as exc:
    #     # 에러가 나면 터미널에 아주 상세하게(Traceback) 다 찍어라!
    #     print("!!!" * 10)
    #     print(f"에러 발생 원인: {exc}")
    #     traceback.print_exc()
    #     print("!!!" * 10)
    #     from fastapi.responses import JSONResponse
    #     return JSONResponse(status_code=500, content={"message": str(exc)})


@app.get("/")
def root():
    return {"message": "Server is running!"}
