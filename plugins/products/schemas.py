from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class ProductCreate(BaseModel):
    seller_id: int
    guild_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    stock: Optional[int] = 0
    custom_metadata: Optional[Dict] = None

    model_config = {"extra": "forbid"}

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    custom_metadata: Optional[Dict] = None
    guild_id: Optional[int] = None

    model_config = {"extra": "forbid"}

class ProductOut(ProductCreate):
    id: int
    created_at: datetime
    updated_at: datetime
