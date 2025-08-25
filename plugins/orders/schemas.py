from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    shipped = "shipped"
    completed = "completed"
    cancelled = "cancelled"

class OrderCreate(BaseModel):
    buyer_id: int
    seller_id: int
    product_ids: List[int]
    total_amount: float

    model_config = {"extra": "forbid"}

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None

    model_config = {"extra": "forbid"}

class OrderOut(BaseModel):
    id: int
    buyer_id: int
    seller_id: int
    product_ids: List[int]
    total_amount: float
    status: OrderStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"extra": "forbid"}