from ..Models.user_model import User
from ..Schemas.user_schema import UserCreateSchema, UserCreateResponseSchema
from sqlalchemy.orm import Session

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: UserCreateSchema) -> UserCreateResponseSchema:
        existing_user = self.db.query(User).filter(User.tg_id == user_data.tg_id).first()
        if existing_user:
            return UserCreateResponseSchema(
                message=f"Welcome Back, {existing_user.tg_username or 'User'}!"
            )
        new_user = User(
            tg_id=user_data.tg_id,
            tg_username=user_data.tg_username
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return UserCreateResponseSchema(
            message=f"Welcome, {new_user.tg_username or 'User'}! Your account has been created."
        )