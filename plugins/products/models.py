from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    price = Column(Float)
    in_stock = Column(Boolean, default=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"))

    # optional: relationship to seller
    # seller = relationship("Seller", back_populates="products")