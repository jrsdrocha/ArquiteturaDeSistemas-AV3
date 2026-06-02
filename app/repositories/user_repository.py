from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    def create(self, username: str, password: str, status: str = "ACTIVE") -> User:
        user = User(username=username, password=password, status=status)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_status(self, user_id: int, status: str) -> Optional[User]:
        user = self.get_by_id(user_id)
        if user is None:
            return None

        user.status = status
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if user is None:
            return False

        self.db.delete(user)
        self.db.commit()
        return True
