from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.Models.clothe_model import FormalityType, SeasonType


class ClotheCreateSchema(BaseModel):
    image_url: str
    name: str
    color: str
    season: SeasonType
    formality: FormalityType


class ClotheUpdateSchema(BaseModel):
    image_url: Optional[str] = None
    name: Optional[str] = None
    color: Optional[str] = None
    season: Optional[SeasonType] = None
    formality: Optional[FormalityType] = None


class ClotheResponseSchema(BaseModel):
    id: int
    user_id: int
    image_url: str
    name: str
    color: str
    season: SeasonType
    formality: FormalityType
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageResponseSchema(BaseModel):
    message: str