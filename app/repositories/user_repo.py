from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate

class UserRepository:
    def get_by_student_id(self, db: Session, student_id: str):
        return db.query(User).filter(User.student_id == student_id).first()

    def create(self, db: Session, user_in: UserCreate, hashed_password: str):
        db_user = User(
            student_id=user_in.student_id,
            name=user_in.name,
            password=hashed_password
        )
        db.add(db_user)
        db.flush()  # DB에 반영하지만 commit은 하지 않음
        return db_user


user_repo = UserRepository()