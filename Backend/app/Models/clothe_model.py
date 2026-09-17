from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.Core.database import Base


class FormalityType(str, Enum):
    CASUAL = "casual"
    FORMAL = "formal"
    HOMEWEAR = "homewear"


class SeasonType(str, Enum):
    SUNNY = "sunny"
    RAINY = "rainy"
    ALL = "all"


class ClotheType(str, Enum):
    TOP = "top"
    BOTTOM = "bottom"
    SHOES = "shoes"
    UNDERWEAR = "underwear"
    HAT = "hat"
    OUTERWEAR = "outerwear"
    ACCESSORY = "accessory"
    OTHER = "other"


class Clothe(Base):
    __tablename__ = "clothes"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    color: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    clothe_type: Mapped[ClotheType] = mapped_column(
        SQLEnum(ClotheType),
        nullable=False,
    )

    season: Mapped[SeasonType] = mapped_column(
        SQLEnum(SeasonType),
        nullable=False,
    )

    formality: Mapped[FormalityType] = mapped_column(
        SQLEnum(FormalityType),
        nullable=False,
    )

    image_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )