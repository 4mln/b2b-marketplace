from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class RFQCreate(BaseModel):
    title: str
    specifications: Optional[Any] = None
    quantity: float
    target_price: Optional[float] = None
    delivery: Optional[str] = None
    expiry: Optional[datetime] = None


class RFQOut(RFQCreate):
    id: int
    buyer_id: int
    created_at: datetime
    updated_at: datetime


class QuoteCreate(BaseModel):
    rfq_id: int
    price: float
    terms: Optional[str] = None
    attachments: Optional[Any] = None


class QuoteOut(QuoteCreate):
    id: int
    seller_id: int
    status: str
    created_at: datetime
    updated_at: datetime


