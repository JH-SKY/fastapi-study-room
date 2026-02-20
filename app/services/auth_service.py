from datetime import datetime, timedelta, timezone
from fastapi import Depends
from app.database import get_db
from app.models.user import User
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession 
from fastapi import HTTPException, status
from app.schemas.user import UserCreate, UserLogin
from app.repositories.user_repo import user_repo 
import bcrypt 
import jwt
from app.database import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class AuthService:
    # 비밀번호 해싱 (동기 작업)
    def _hash_password(self, password: str) -> str:
        pw_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(pw_bytes, salt)
        return hashed_pw.decode("utf-8")

    # 회원가입 로직
    async def signup(self, db: AsyncSession, data: UserCreate):
        # [STEP 1] 중복 검사
        existing_user = await user_repo.get_by_student_id(db, student_id=data.student_id)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 가입된 학번입니다.",
            )

        # [STEP 2] 비밀번호 해싱
        hashed_password = self._hash_password(data.password)

        # [STEP 3] 트랜잭션 시작 (with 문으로 통일)
        async with db.begin():
            new_user = await user_repo.create(
                db, user_in=data, hashed_password=hashed_password
            )
            # 블록 종료 시 자동 commit, 에러 발생 시 자동 rollback

        # [STEP 4] 데이터 동기화
        await db.refresh(new_user)
        return new_user
    
    # 엑세스 토큰 생성
    def _create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # 로그인 로직
    async def login(self, db: AsyncSession, data: UserLogin):
        user = await user_repo.get_by_student_id(db, student_id=data.student_id)
        
        # 비밀번호 검증
        if not user or not bcrypt.checkpw(data.password.encode("utf-8"), user.password.encode("utf-8")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="학번 또는 비밀번호가 일치하지 않습니다.",
            )

        # 관리자 권한(role) 정보를 포함하여 토큰 발행
        access_token = self._create_access_token(
            data={"sub": user.student_id, "role": user.role}
        )
        
        return {"access_token": access_token, "token_type": "bearer"}

    # 초기 관리자 생성 로직 (필요 시 주석 해제하여 사용)
    # async def create_initial_admin(self, db: AsyncSession):
    #     admin_id = "admin"
    #     existing_admin = await user_repo.get_by_student_id(db, student_id=admin_id)
        
    #     if not existing_admin:
    #         print("🚀 관리자 계정 생성 중...")
    #         hashed_pw = self._hash_password("admin1234") 
            
    #         from app.models.user import User
    #         async with db.begin():
    #             admin_user = User(
    #                 student_id=admin_id,
    #                 name="최고관리자",
    #                 password=hashed_pw,
    #                 role="admin"
    #             )
    #             db.add(admin_user)
    #         print("✅ 관리자 계정(role: admin) 생성 완료!")

auth_service = AuthService()

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 유효하지 않습니다.",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        student_id: str = payload.get("sub")
        if student_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = await user_repo.get_by_student_id(db, student_id=student_id)
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요한 서비스입니다."
        )
    return current_user