from fastapi import APIRouter, Body, Cookie, Depends, Response
from sqlalchemy.orm import Session

from app.Auth.jwt import verify_access_token
from app.Core.database import get_db
from app.Schemas.user_schema import (
    AddApiKey,
    LoginUserSchema,
    UserCreateResponseSchema,
    UserCreateSchema,
    AddLocation
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

@router.post("/logout")
def logout_endpoint(
    response: Response,
):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=False,  # True in production with HTTPS
        samesite="lax",
    )

    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=False,  # True in production with HTTPS
        samesite="lax",
    )

    return {
        "message": "Logout successful",
    }

@router.patch("/api-keys")
def set_api_key_endpoint(
    api_key: AddApiKey,
    user_id: int = Depends(verify_access_token),
    db: Session = Depends(get_db),
):
    user_service = UserService(db)

    return user_service.set_api_key(
        user_id=user_id,
        api_key=api_key,
    )

@router.patch("/location")
def add_location_endpoint(
    location: AddLocation,
    user_id: int = Depends(verify_access_token),
    db: Session = Depends(get_db),
):
    user_service = UserService(db)

    return user_service.add_location(
        user_id=user_id,
        location=location,
    )