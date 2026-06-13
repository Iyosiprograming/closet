from ..Models.clothe_model import Clothe
from sqlalchemy.orm import Session
from ..Schemas.clothe_schema import ClotheCreateSchema, ClotheCreateResponseSchema

class ClotheService:
    def __init__(self, db: Session):
        self.db = db

    def add_new_clothe(self, clothe_data: ClotheCreateSchema) -> ClotheCreateResponseSchema:
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
        
        return ClotheCreateResponseSchema(message="Clothe added successfully")