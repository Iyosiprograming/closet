from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.Core.logger import logger
from app.Models.clothe_model import Clothe
from app.Models.user_model import User
from app.Schemas.clothe_schema import (
    ClotheResponseSchema,
    MessageResponseSchema,
)
from app.Models.clothe_model import FormalityType, SeasonType


IMAGE_DIR = Path("images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)


class ClotheService:
    def __init__(self, db: Session):
        self.db = db

    def _save_image(self, image: UploadFile) -> str:
        try:
            if not image.content_type or not image.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File must be an image",
                )

            extension = Path(image.filename or "").suffix.lower()

            if not extension:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Image must have a valid extension",
                )

            filename = f"{uuid4()}{extension}"
            file_path = IMAGE_DIR / filename

            with file_path.open("wb") as buffer:
                while chunk := image.file.read(1024 * 1024):
                    buffer.write(chunk)

            return f"/images/{filename}"

        except HTTPException:
            raise

        except OSError:
            logger.exception("Error while saving image")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not save image",
            )

    def _delete_image(self, image_url: str | None) -> None:
        if not image_url:
            return

        filename = Path(image_url).name
        file_path = IMAGE_DIR / filename

        try:
            if file_path.exists():
                file_path.unlink()

        except OSError:
            logger.exception(
                "Could not delete image: %s",
                file_path,
            )

    def check_user_by_id(self, user_id: int) -> bool:
        try:
            return (
                self.db.query(User)
                .filter(User.id == user_id)
                .first()
                is not None
            )

        except SQLAlchemyError:
            logger.exception("Database error while checking user")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            )

    def add_new_clothe(
        self,
        image: UploadFile,
        name: str,
        color: str,
        season: SeasonType,
        formality: FormalityType,
        user_id: int,
    ) -> ClotheResponseSchema:
        image_url = None

        try:
            if not self.check_user_by_id(user_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            image_url = self._save_image(image)

            new_clothe = Clothe(
                user_id=user_id,
                image_url=image_url,
                name=name,
                color=color,
                season=season,
                formality=formality,
            )

            self.db.add(new_clothe)
            self.db.commit()
            self.db.refresh(new_clothe)

            logger.info(
                "Clothe created successfully: id=%s user_id=%s",
                new_clothe.id,
                user_id,
            )

            return ClotheResponseSchema.model_validate(new_clothe)

        except HTTPException:
            raise

        except SQLAlchemyError:
            self.db.rollback()

            if image_url:
                self._delete_image(image_url)

            logger.exception(
                "Database error while creating clothe: user_id=%s",
                user_id,
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            )

    def update_clothe(
        self,
        clothe_id: int,
        user_id: int,
        image: UploadFile | None = None,
        name: str | None = None,
        color: str | None = None,
        season: SeasonType | None = None,
        formality: FormalityType | None = None,
    ) -> ClotheResponseSchema:
        new_image_url = None
        old_image_url = None

        try:
            clothe = (
                self.db.query(Clothe)
                .filter(
                    Clothe.id == clothe_id,
                    Clothe.user_id == user_id,
                )
                .first()
            )

            if not clothe:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Clothe not found",
                )

            if image:
                new_image_url = self._save_image(image)
                old_image_url = clothe.image_url
                clothe.image_url = new_image_url

            if name is not None:
                clothe.name = name

            if color is not None:
                clothe.color = color

            if season is not None:
                clothe.season = season

            if formality is not None:
                clothe.formality = formality

            self.db.commit()
            self.db.refresh(clothe)

            # Delete old image only after successful DB commit.
            if old_image_url:
                self._delete_image(old_image_url)

            logger.info(
                "Clothe updated successfully: id=%s user_id=%s",
                clothe_id,
                user_id,
            )

            return ClotheResponseSchema.model_validate(clothe)

        except HTTPException:
            if new_image_url:
                self._delete_image(new_image_url)

            raise

        except SQLAlchemyError:
            self.db.rollback()

            if new_image_url:
                self._delete_image(new_image_url)

            logger.exception(
                "Database error while updating clothe: id=%s",
                clothe_id,
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            )

    def delete_clothe(
        self,
        clothe_id: int,
        user_id: int,
    ) -> MessageResponseSchema:
        try:
            clothe = (
                self.db.query(Clothe)
                .filter(
                    Clothe.id == clothe_id,
                    Clothe.user_id == user_id,
                )
                .first()
            )

            if not clothe:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Clothe not found",
                )

            image_url = clothe.image_url

            self.db.delete(clothe)
            self.db.commit()

            self._delete_image(image_url)

            logger.info(
                "Clothe deleted successfully: id=%s user_id=%s",
                clothe_id,
                user_id,
            )

            return MessageResponseSchema(
                message="Clothe deleted successfully"
            )

        except HTTPException:
            raise

        except SQLAlchemyError:
            self.db.rollback()

            logger.exception(
                "Database error while deleting clothe: id=%s",
                clothe_id,
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            )

    def get_clothe(
        self,
        clothe_id: int,
        user_id: int,
    ) -> ClotheResponseSchema:
        try:
            clothe = (
                self.db.query(Clothe)
                .filter(
                    Clothe.id == clothe_id,
                    Clothe.user_id == user_id,
                )
                .first()
            )

            if not clothe:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Clothe not found",
                )

            return ClotheResponseSchema.model_validate(clothe)

        except HTTPException:
            raise

        except SQLAlchemyError:
            logger.exception(
                "Database error while getting clothe: id=%s user_id=%s",
                clothe_id,
                user_id,
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            )

    def get_all_clothes(
        self,
        user_id: int,
    ) -> list[ClotheResponseSchema]:
        try:
            clothes = (
                self.db.query(Clothe)
                .filter(Clothe.user_id == user_id)
                .all()
            )

            return [
                ClotheResponseSchema.model_validate(clothe)
                for clothe in clothes
            ]

        except SQLAlchemyError:
            logger.exception(
                "Database error while getting clothes: user_id=%s",
                user_id,
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            )

