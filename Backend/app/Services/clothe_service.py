from ..Models.clothe_model import Clothe
from ..Models.user_model import User
from sqlalchemy.orm import Session
from typing import List
from ..Schemas.clothe_schema import ClotheCreateSchema, MessageResponseSchema

class ClotheService:
    def __init__(self, db: Session):
        self.db = db

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
    
    def get_all_clothe(self, user_id: int) -> List[Clothe]:
        return self.db.query(Clothe).filter(Clothe.user_id == user_id).all()
    
    def delete_clothe(self, user_id: int, clothe_id: int) -> MessageResponseSchema:

        existing_user = self.db.query(User).filter(User.tg_id == user_id).first()
        if not existing_user:
            return MessageResponseSchema(message="User not found")    
        delete_count = self.db.query(Clothe).filter(Clothe.id == clothe_id).delete()
        if delete_count == 0:
            return MessageResponseSchema(message="Clothe not found")    
        self.db.commit()
        return MessageResponseSchema(message="Clothe deleted successfully")

    # update and delete clothes

    # get suggestions