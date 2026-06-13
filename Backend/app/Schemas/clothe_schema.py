from pydantic import BaseModel
from typing import Optional

class ClotheCreateSchema(BaseModel):
    user_id: int
    image_url: str
    name: Optional[str] = None
    color: str
    category: str
    condition_tier: Optional[int] = None
    description: str

class ClotheCreateResponseSchema(BaseModel):
    message: str