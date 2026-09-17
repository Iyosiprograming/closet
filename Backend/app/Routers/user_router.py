from fastapi import APIRouter, Cookie, Depends, Response
from sqlalchemy.orm import Session

from app.Core.database import get_db
from app.Schemas.user_schema import (
    LoginUserSchema,
    UserCreateResponseSchema,
    UserCreateSchema,
)
from app.Services.user_service import UserService


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/", response_model=UserCreateResponseSchema)
def create_user_endpoint(
    user_data: UserCreateSchema,
    db: Session = Depends(get_db),
):
    user_service = UserService(db)

    return user_service.create_user(user_data)


@router.post("/login")
def login_user_endpoint(
    user_data: LoginUserSchema,
    response: Response,
    db: Session = Depends(get_db),
):
    user_service = UserService(db)

    access_token, refresh_token = user_service.login_user(user_data)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # True in production with HTTPS
        samesite="lax",
        max_age=15 * 60,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # True in production with HTTPS
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
    )

    return {
        "message": "Login successful",
    }


@router.post("/refresh")
def refresh_access_token_endpoint(
    response: Response,
    refresh_token: str = Cookie(...),
    db: Session = Depends(get_db),
):
    user_service = UserService(db)

    new_access_token = user_service.refresh_access_token(refresh_token)

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=False,  # True in production with HTTPS
        samesite="lax",
        max_age=15 * 60,
    )

    return {
        "message": "Token refreshed",
    }