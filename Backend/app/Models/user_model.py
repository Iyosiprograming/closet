from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.Core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )

    password: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    gemini_api_key: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    openweather_api_key: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )