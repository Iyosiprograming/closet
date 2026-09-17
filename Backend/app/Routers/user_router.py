from fastapi import APIRouter, Depends, Response
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


@router.post(
    "/",
    response_model=UserCreateResponseSchema,
)
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

    token = user_service.login_user(user_data)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
    )

    return {"message": "Login successful"}