from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TransactionBase(BaseModel):
    user_id: int
    amount: float
    currency: Optional[str] = "USD"
    status: Optional[str] = "pending"

class TransactionCreate(TransactionBase):
    payment_method: str

class TransactionOut(TransactionBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
