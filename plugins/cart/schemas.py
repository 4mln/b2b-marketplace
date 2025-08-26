# plugins/cart/schemas.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class CartCreate(BaseModel):
    user_id: int
    items: Optional[List[CartItemCreate]] = []

class CartOut(BaseModel):
    id: int
    user_id: int
    is_active: bool
    items: List[CartItemOut]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
