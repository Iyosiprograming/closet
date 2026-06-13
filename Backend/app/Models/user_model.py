from ..database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    tg_id = Column(Integer, primary_key=True, index=True)
    tg_username = Column(String, nullable=True)

    clothes = relationship("Clothe", back_populates="user")