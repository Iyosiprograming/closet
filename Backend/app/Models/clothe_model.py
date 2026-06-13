from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Clothe(Base):
    __tablename__ = "clothes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.tg_id"), nullable=False)
    
    image_url = Column(String(500), nullable=False)
    name = Column(String(100), nullable=True)
    color = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False) 
    
    # Tracks item status (e.g., 1=Casual, 2=Formal/Party, 3=New)
    condition_tier = Column(Integer, nullable=True) 
    description = Column(String(500), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="clothes")