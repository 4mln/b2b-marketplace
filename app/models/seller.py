from sqlalchemy import Column, Integer, String, Float
from app.db.base import Base

class Seller(Base):
    __tablename__ = "sellers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    rating = Column(Float, default=0.0)