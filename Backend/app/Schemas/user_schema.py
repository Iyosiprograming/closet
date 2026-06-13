from pydantic import BaseModel
from typing import Optional

class UserCreateSchema(BaseModel):
    tg_id: int
    tg_username: Optional[str] = None

class UserCreateResponseSchema(BaseModel):
    message: str