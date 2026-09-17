from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.Auth.jwt import verify_access_token
from app.Core.database import get_db
from app.Models.clothe_model import (
    ClotheType,
    FormalityType,
    SeasonType,
)
from app.Schemas.clothe_schema import (
    ClotheResponseSchema,
    MessageResponseSchema,
)
from app.Services.clothe_service import ClotheService


router = APIRouter(
    prefix="/clothes",
    tags=["clothes"],
)


@router.post(
    "/",
    response_model=ClotheResponseSchema,
)
def add_new_clothe_endpoint(
    image: UploadFile = File(...),
    name: str = Form(...),
    color: str = Form(...),
    clothe_type: ClotheType = Form(...),
    season: SeasonType = Form(...),
    formality: FormalityType = Form(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_access_token),
):
    clothe_service = ClotheService(db)

    return clothe_service.add_new_clothe(
        image=image,
        name=name,
        color=color,
        clothe_type=clothe_type,
        season=season,
        formality=formality,
        user_id=user_id,
    )


@router.get(
    "/",
    response_model=list[ClotheResponseSchema],
)
def get_all_clothes_endpoint(
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_access_token),
):
    clothe_service = ClotheService(db)

    return clothe_service.get_all_clothes(
        user_id=user_id,
    )


@router.get(
    "/{clothe_id}",
    response_model=ClotheResponseSchema,
)
def get_single_clothe_endpoint(
    clothe_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_access_token),
):
    clothe_service = ClotheService(db)

    return clothe_service.get_clothe(
        clothe_id=clothe_id,
        user_id=user_id,
    )


@router.patch(
    "/{clothe_id}",
    response_model=ClotheResponseSchema,
)
def update_clothe_endpoint(
    clothe_id: int,
    image: UploadFile | None = File(None),
    name: str | None = Form(None),
    color: str | None = Form(None),
    clothe_type: ClotheType | None = Form(None),
    season: SeasonType | None = Form(None),
    formality: FormalityType | None = Form(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_access_token),
):
    clothe_service = ClotheService(db)

    return clothe_service.update_clothe(
        clothe_id=clothe_id,
        user_id=user_id,
        image=image,
        name=name,
        color=color,
        clothe_type=clothe_type,
        season=season,
        formality=formality,
    )


@router.delete(
    "/{clothe_id}",
    response_model=MessageResponseSchema,
)
def delete_clothe_endpoint(
    clothe_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_access_token),
):
    clothe_service = ClotheService(db)

    return clothe_service.delete_clothe(
        clothe_id=clothe_id,
        user_id=user_id,
    )