from sqlalchemy import Column, Integer, Float, String, Enum as SQLAEnum, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession
from plugins.orders.models import Order
from enum import Enum
from sqlalchemy.orm import declarative_base

Base = declarative_base()  # or import centralized Base from app.core.db

class PaymentStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    amount = Column(Float, nullable=False)
    provider = Column(String, nullable=False)  # e.g., stripe, paypal
    status = Column(SQLAEnum(PaymentStatus), default=PaymentStatus.pending, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    order = relationship("Order", backref="payments")