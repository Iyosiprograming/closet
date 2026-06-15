from ..Models.clothe_model import Clothe
from ..Models.user_model import User
from sqlalchemy.orm import Session
from typing import List
from ..Schemas.clothe_schema import ClotheCreateSchema, MessageResponseSchema
from ..helper.logic import generate_response

class ClotheService:
    def __init__(self, db: Session):
        self.db = db

# this function addes clothe to the system for user
    def add_new_clothe(self, clothe_data: ClotheCreateSchema) -> MessageResponseSchema:
        description_str = f"{clothe_data.name or ''} {clothe_data.color} {clothe_data.category} {clothe_data.condition_tier or ''}".strip()
        
        new_clothe = Clothe(
            user_id=clothe_data.user_id,
            image_url=clothe_data.image_url,
            name=clothe_data.name,
            color=clothe_data.color,
            category=clothe_data.category,
            condition_tier=clothe_data.condition_tier,
            description=description_str  
        )
        
        self.db.add(new_clothe)
        self.db.commit()
        self.db.refresh(new_clothe)
        
        return MessageResponseSchema(message="Clothe added successfully")
    
    # get single clothe
    def get_single_clothe(self, clothe_id, user_id):
        existing_user = self.db.query(User).filter(User.tg_id == user_id).first()
        if not existing_user:
            return MessageResponseSchema(message="User Not Found")
        
        existing_clothe = self.db.query(Clothe).filter(Clothe.id == clothe_id).first()

        if not existing_clothe:
            return MessageResponseSchema(message="Clothe Not Found")
        
        return existing_clothe
    
    # this fucntion get all the existing clothe for user
    def get_all_clothe(self, user_id: int) -> List[Clothe]:
        return self.db.query(Clothe).filter(Clothe.user_id == user_id).all()
    
    # this function removes users clothe
    def delete_clothe(self, user_id: int, clothe_id: int) -> MessageResponseSchema:

        existing_user = self.db.query(User).filter(User.tg_id == user_id).first()
        if not existing_user:
            return MessageResponseSchema(message="User not found")    
        delete_count = self.db.query(Clothe).filter(Clothe.id == clothe_id).delete()
        if delete_count == 0:
            return MessageResponseSchema(message="Clothe not found")    
        self.db.commit()
        return MessageResponseSchema(message="Clothe deleted successfully")

    
# this function is the logic to update the existing clothes
    def update_clothe(self, clothe_data: ClotheCreateSchema, user_id: int, clothe_id: int) -> MessageResponseSchema:
        existing_user = self.db.query(User).filter(User.tg_id == user_id).first()
        if not existing_user:
            return MessageResponseSchema(message="User not found")
        
        existing_clothe = self.db.query(Clothe).filter(Clothe.id == clothe_id, Clothe.user_id == user_id).first()
        if not existing_clothe:
            return MessageResponseSchema(message="Clothing item not found")
        
        for key, value in clothe_data.model_dump(exclude_unset=True).items():
            setattr(existing_clothe, key, value)
        
        self.db.commit()
        self.db.refresh(existing_clothe)
        
        return MessageResponseSchema(message="Clothing item updated successfully")

        # get suggestions

    async def suggest_clothe(self, prompt: str, user_id: int):
        existing_user = (
            self.db.query(User)
            .filter(User.tg_id == user_id)
            .first()
        )

        if not existing_user:
            return MessageResponseSchema(
                message="User not found"
            )

        all_clothes = self.get_all_clothe(user_id)

        if not all_clothes:
            return MessageResponseSchema(
                message="No clothes found"
            )

        clothe_descriptions = [
            f"ID {item.id}: {item.description}"
            for item in all_clothes
        ]

        suggestion = await generate_response(
        clothe_descriptions,
        prompt
    )

        clothe_ids = suggestion.get("clothe_ids", [])
        if not clothe_ids:
            return MessageResponseSchema(
                message="Could not generate a recommendation"
            )

        selected_clothes = (
            self.db.query(Clothe)
            .filter(Clothe.id.in_(clothe_ids), Clothe.user_id == user_id)
            .all()
        )

        return {
            "outfit": selected_clothes,
        }
         