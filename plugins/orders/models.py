from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, Enum as SQLAEnum
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from plugins.orders.schemas import OrderStatus

Base = declarative_base()  # or import from your app.core.db Base if centralized

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, nullable=False)
    seller_id = Column(Integer, nullable=False)
    product_ids = Column(JSON, nullable=False)  # store list of product IDs
    total_amount = Column(Float, nullable=False)
    status = Column(SQLAEnum(OrderStatus), default=OrderStatus.pending, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())