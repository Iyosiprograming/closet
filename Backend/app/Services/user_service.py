from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.Auth.jwt import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from app.Auth.password import hash_password, verify_password
from app.Core.logger import logger
from app.Models.user_model import User
from app.Schemas.user_schema import (
    LoginUserSchema,
    UserCreateResponseSchema,
    UserCreateSchema,
    AddApiKey,
    AddLocation
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

    def login_user(
        self,
        user_data: LoginUserSchema,
    ) -> tuple[str, str]:
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

            access_token = create_access_token(user.id)
            refresh_token = create_refresh_token(user.id)

            logger.info(
                "User logged in successfully: %s",
                user.username,
            )

            return access_token, refresh_token

        except HTTPException:
            raise

        except SQLAlchemyError:
            self.db.rollback()

            logger.exception(
                "Database error while logging in user"
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            )

    def refresh_access_token(
        self,
        refresh_token: str,
    ) -> str:
        try:
            user_id = verify_refresh_token(refresh_token)

            user_exists = (
                self.db.query(User.id)
                .filter(User.id == user_id)
                .first()
                is not None
            )

            if not user_exists:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                )

            return create_access_token(user_id)

        except HTTPException:
            raise

        except SQLAlchemyError:
            logger.exception(
                "Database error while refreshing access token"
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            )

    def set_api_key(
        self,
        user_id: int,
        api_key: AddApiKey,
    ):
        try:
            user = (
                self.db.query(User)
                .filter(User.id == user_id)
                .first()
            )

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            # Required
            user.gemini_api_key = api_key.gemini_api_key

            # Optional
            if api_key.openweather_api_key is not None:
                user.openweather_api_key = api_key.openweather_api_key

            self.db.commit()
            self.db.refresh(user)

            logger.info(
                "API keys updated for user %s",
                user_id,
            )

            return {
                "message": "API keys updated successfully"
            }

        except HTTPException:
            raise

        except SQLAlchemyError:
            self.db.rollback()

            logger.exception(
                "Database error while setting API keys for user %s",
                user_id,
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            )

    def add_location(
        self,
        user_id: int,
        location: AddLocation,
    ):
        try:
            user = (
                self.db.query(User)
                .filter(User.id == user_id)
                .first()
            )

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            user.location = location.location

            self.db.commit()
            self.db.refresh(user)

            logger.info(
                "Location updated for user %s",
                user_id,
            )

            return {
                "message": "Location updated successfully",
            }

        except HTTPException:
            raise

        except SQLAlchemyError:
            self.db.rollback()

            logger.exception(
                "Database error while updating location for user %s",
                user_id,
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            )