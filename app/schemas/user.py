from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


# 1. 공통 필드를 모아둔 부모 스키마
class UserBase(BaseModel):
    student_id: str = Field(
        min_length=8, max_length=8, description="학번 8자리", examples=["20260101"]
    )
    name: str = Field(min_length=2, max_length=20, description="사용자 실명")


# 2. 회원가입 시 사용 (Base 상속 + 비밀번호 추가)
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=100)

    @field_validator("student_id")
    @classmethod
    def validate_student_id(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("학번은 숫자만 입력 가능합니다.")

        current_year = datetime.now().year
        year = int(v[:4])
        if year < 2020 or year > current_year:
            raise ValueError(
                f"입학 연도는 2020년부터 {current_year}년 사이여야 합니다."
            )

        dept_code = int(v[4:6])
        if not (1 <= dept_code <= 15):
            raise ValueError("존재하지 않는 학과 번호입니다. (01~15)")

        if int(v[6:8]) == 0:
            raise ValueError("유효하지 않은 개인 순번입니다.")
        return v

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if not any(char.isalpha() for char in v) or not any(
            char.isdigit() for char in v
        ):
            raise ValueError("비밀번호는 영문자와 숫자를 최소 하나씩 포함해야 합니다.")
        return v


# 3. 로그인 시 사용 (학번과 비밀번호만 필요)
class UserLogin(BaseModel):
    student_id: str
    password: str


# 4. 정보 수정 시 사용 (모든 필드를 선택사항으로 설정)
class UserUpdate(BaseModel):
    # 수정하고 싶은 것만 보낼 수 있게 Optional 사용
    name: Optional[str] = Field(None, min_length=2, max_length=20)
    password: Optional[str] = Field(None, min_length=8, max_length=100)


# 5. 데이터 조회(응답) 시 사용
class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
