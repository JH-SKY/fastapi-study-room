from sqlalchemy.ext.asyncio import AsyncSession # Session 대신 AsyncSession
from fastapi import HTTPException, status
from app.schemas.user import UserCreate
from app.repositories.user_repo import user_repo 
import bcrypt 

class AuthService:
    # 비밀번호 해싱은 CPU 작업이므로 async가 아니어도 됩니다.
    def _hash_password(self, password: str) -> str:
        pw_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(pw_bytes, salt)
        return hashed_pw.decode("utf-8")

    # 1. async def로 변경
    async def signup(self, db: AsyncSession, data: UserCreate):
        # 2. 비동기에서는 with db.begin() 대신 직접 commit/rollback을 관리하거나 
        # 레포지토리에서 처리하도록 합니다. 
        
        # [STEP 1] 중복 검사 (await 필수!)
        # user_repo.get_by_student_id도 async 함수여야 합니다.
        existing_user = await user_repo.get_by_student_id(db, student_id=data.student_id)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 가입된 학번입니다.",
            )

        # [STEP 2] 비밀번호 해싱
        hashed_password = self._hash_password(data.password)

        # [STEP 3] 사용자 객체 생성 및 저장 (await 필수!)
        new_user = await user_repo.create(
            db, user_in=data, hashed_password=hashed_password
        )

        # [STEP 4] 트랜잭션 확정 및 새로고침 (await 필수!)
        try:
            await db.commit()   # 비동기 커밋
            await db.refresh(new_user) # 비동기 새로고침
        except Exception as e:
            await db.rollback() # 에러 시 비동기 롤백
            raise e

        return new_user
    

    # 관리자계정 생성 로직 (비동기 버전)
    # async def create_initial_admin(self, db: AsyncSession):
    #     admin_id = "admin"
    #     # 1. 이미 있는지 확인
    #     existing_admin = await user_repo.get_by_student_id(db, student_id=admin_id)
        
    #     if not existing_admin:
    #         print("🚀 관리자 계정 생성 중...")
    #         hashed_pw = self._hash_password("admin1234") 
            
    #         # User 모델 객체를 직접 생성하면서 role을 'admin'으로 설정
    #         from app.models.user import User
    #         admin_user = User(
    #             student_id=admin_id,
    #             name="최고관리자",
    #             password=hashed_pw,
    #             role="admin"  # <--- 여기서 권한을 직접 부여!
    #         )
            
    #         db.add(admin_user)
    #         await db.commit()
    #         print("✅ 관리자 계정(role: admin) 생성 완료!")

auth_service = AuthService()