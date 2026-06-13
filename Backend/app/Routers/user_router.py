from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..Services.user_service import UserService
from ..Schemas.user_schema import UserCreateSchema, UserCreateResponseSchema

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserCreateResponseSchema)
def create_user_endpoint(user_data: UserCreateSchema, db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.create_user(user_data)