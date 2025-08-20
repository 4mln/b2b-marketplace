from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SAEnum
from app.db.base import Base
from plugins.seller.schemas import SubscriptionType  # 🔗 reuse same Enum

class Seller(Base):
    __tablename__ = "sellers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1024), nullable=True)
    banner_url = Column(String(512), nullable=True)
    subscription_type = Column(SAEnum(SubscriptionType, name="subscription_type_enum"), nullable=True)
    rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="sellers")