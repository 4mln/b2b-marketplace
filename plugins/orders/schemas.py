from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"
    refunded = "refunded"


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = Field(None, gt=0)


class OrderItemOut(OrderItemBase):
    id: int
    subtotal: float

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    seller_id: int
    items: List[OrderItemCreate]
    shipping_address: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    shipping_address: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class OrderOut(OrderBase):
    id: int
    buyer_id: int
    status: OrderStatus
    total_amount: float
    items: List[OrderItemOut]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True