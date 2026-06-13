from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..Services.clothe_service import ClotheService
from ..Schemas.clothe_schema import ClotheCreateSchema, ClotheCreateResponseSchema

router = APIRouter(prefix="/clothes", tags=["clothes"])

@router.post("/", response_model=ClotheCreateResponseSchema)
def add_new_clothe_endpoint(clothe_data: ClotheCreateSchema, db: Session = Depends(get_db)):
    clothe_service = ClotheService(db)
    return clothe_service.add_new_clothe(clothe_data)

@router.post("/all", response_model=list[ClotheCreateSchema])
def get_all_clothe_endpoint(user_id: int, db: Session = Depends(get_db)):
    clothe_service = ClotheService(db)
    return clothe_service.get_all_clothe(user_id)