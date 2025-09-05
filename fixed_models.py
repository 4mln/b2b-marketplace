from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, func, JSON
from sqlalchemy.orm import relationship, declarative_base

from app.db.base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    guild_id = Column(Integer, ForeignKey("guilds.id"), nullable=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    custom_metadata = Column(JSON, nullable=True)  # optional extra info
    status = Column(String, default="pending", nullable=False)  # pending, approved, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    seller = relationship("Seller")