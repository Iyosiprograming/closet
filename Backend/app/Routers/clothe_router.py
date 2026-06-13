from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..Services.clothe_service import ClotheService
from ..Schemas.clothe_schema import ClotheCreateSchema, MessageResponseSchema

router = APIRouter(prefix="/clothes", tags=["clothes"])

@router.post("/", response_model=MessageResponseSchema)
def add_new_clothe_endpoint(clothe_data: ClotheCreateSchema, db: Session = Depends(get_db)):
    clothe_service = ClotheService(db)
    return clothe_service.add_new_clothe(clothe_data)

@router.post("/all", response_model=list[ClotheCreateSchema])
def get_all_clothe_endpoint(user_id: int, db: Session = Depends(get_db)):
    clothe_service = ClotheService(db)
    return clothe_service.get_all_clothe(user_id)

@router.delete("/", response_model=MessageResponseSchema)
def delete_clothe_endpoint(user_id: int, clothe_id: int, db: Session = Depends(get_db)):
    clothe_service = ClotheService(db)
    return clothe_service.delete_clothe(user_id,clothe_id)

@router.put("/", response_model=MessageResponseSchema)
def update_clothe_endpoint(clothe_data: ClotheCreateSchema, user_id: int, clothe_id: int, db: Session = Depends(get_db)):
    clothe_service = ClotheService(db)
    return clothe_service.update_clothe(clothe_data, user_id, clothe_id)