from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, func, JSON
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()  # or import centralized Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    custom_metadata = Column(JSON, nullable=True)  # optional extra info
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    seller = relationship("Seller")
