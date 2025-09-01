from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, func
from sqlalchemy.orm import declarative_base


from app.db.base import Base


class Escrow(Base):
    __tablename__ = "escrows"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="IRR")
    status = Column(String, default="held")  # held, released, refunded
    created_at = Column(DateTime(timezone=True), server_default=func.now())








