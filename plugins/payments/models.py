from sqlalchemy import Column, Integer, Float, String, DateTime, func
from app.db.base import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    status = Column(String, default="pending")
    payment_method = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
