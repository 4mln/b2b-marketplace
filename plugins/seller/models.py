from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, JSON, func
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class Seller(Base):
    __tablename__ = "sellers"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    subscription = Column(String, nullable=False, default="basic")  # basic, premium, vip
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Storefront features
    store_url = Column(String, nullable=True)  # Custom store URL
    store_policies = Column(JSON, nullable=True)  # Store policies as JSON
    is_featured = Column(Boolean, default=False)  # Featured seller flag
    is_verified = Column(Boolean, default=False)  # Verified seller flag
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship to User (owner)
    user = relationship("User", back_populates="sellers")
    
    # Relationships to other entities
    products = relationship("Product", back_populates="seller", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="seller", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="seller", cascade="all, delete-orphan")
