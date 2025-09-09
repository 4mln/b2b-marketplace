from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, Enum as SQLAEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from plugins.orders.schemas import OrderStatus

from app.db.base import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Add FK if needed
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)  # <-- Add FK here
    product_ids = Column(JSON, nullable=False)  # store list of product items with quantity and price
    total_amount = Column(Float, nullable=False)
    status = Column(SQLAEnum(OrderStatus), default=OrderStatus.pending, nullable=False)
    shipping_address = Column(JSON, nullable=True)  # store shipping address as JSON
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    seller = relationship("Seller", back_populates="orders")
    buyer = relationship("User", back_populates="buyer_orders")
