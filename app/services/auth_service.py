from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.schemas.user import UserCreate  # Pydantic 모델
from app.repositories.user_repo import user_repo  # 사용자 레포지토리 임포트
import bcrypt  


class AuthService:
    def _hash_password(self, password: str) -> str:
        # bcrypt는 바이트 타입을 입력받으므로 .encode() 필요
        # 한줄짜리 코드랑 100% 같은 코드 풀어서 4줄짜리로 작성 한거임
        pw_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(pw_bytes, salt)
        return hashed_pw.decode("utf-8")

    def signup(self, db: Session, data: UserCreate):
        # 트랜잭션 시작 - with 블록이 끝나면 자동으로 commit 또는 rollback이 됩니다.
        with db.begin():
            # 1. 중복 검사 (레포지토리에 전담 비서처럼 시키기)
            existing_user = user_repo.get_by_student_id(db, student_id=data.student_id)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="이미 가입된 학번입니다.",
                )

            # 2. 비밀번호 해싱
            hashed_password = self._hash_password(data.password)

            # 3. 사용자 객체 생성 및 저장
            # 레포지토리의 create 메서드를 호출하여 저장 로직을 분리합니다.
            new_user = user_repo.create(
                db, user_in=data, hashed_password=hashed_password
            )

            # with 블록이 끝나면 자동으로 db.commit()이 호출됩니다.

        # 트랜잭션 밖에서 최신 데이터로 새로고침
        db.refresh(new_user)
        return new_user


auth_service = AuthService()
