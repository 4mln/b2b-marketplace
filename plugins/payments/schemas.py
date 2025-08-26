from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class PaymentStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"

class PaymentCreate(BaseModel):
    order_id: int
    amount: float
    provider: str

    model_config = {"extra": "forbid"}

class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None

    model_config = {"extra": "forbid"}

class PaymentOut(BaseModel):
    id: int
    order_id: int
    amount: float
    provider: str
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"extra": "forbid"}
    