from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.Auth.password import hash_password, verify_password
from app.Auth.jwt import create_access_token
from app.Core.logger import logger
from app.Models.user_model import User
from app.Schemas.user_schema import (
    UserCreateResponseSchema,
    UserCreateSchema,
    LoginUserSchema
)


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def user_exist(self, username: str) -> bool:
        try:
            return (
                self.db.query(User)
                .filter(User.username == username)
                .first()
                is not None
            )
        except SQLAlchemyError:
            logger.exception("Database error while checking username")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            )

    def create_user(
        self,
        user_data: UserCreateSchema,
    ) -> UserCreateResponseSchema:
        try:
            if self.user_exist(user_data.username):
                logger.warning(
                    "User registration attempted with existing username: %s",
                    user_data.username,
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already exists",
                )

            hashed_password = hash_password(user_data.password)

            new_user = User(
                username=user_data.username,
                password=hashed_password,
            )

            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)

            logger.info(
                "User created successfully: %s",
                new_user.username,
            )

            return UserCreateResponseSchema(
                id=new_user.id,
                username=new_user.username,
            )

        except IntegrityError:
            self.db.rollback()

            logger.exception(
                "Database integrity error while creating user"
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

        except SQLAlchemyError:
            self.db.rollback()

            logger.exception(
                "Database error while creating user"
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            )
    def login_user(self, user_data: LoginUserSchema):
        try:
            user = (
                self.db.query(User)
                .filter(User.username == user_data.username)
                .first()
            )

            if not user or not verify_password(
                user_data.password,
                user.password,
            ):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password",
                )

            token = create_access_token(user.id)

            logger.info("User logged in successfully: %s", user.username)

            return token

        except SQLAlchemyError:
            self.db.rollback()

            logger.exception("Database error while logging in user")

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            )
