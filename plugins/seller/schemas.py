# plugins/seller/schemas.py
from enum import Enum
from pydantic import BaseModel
from typing import Optional

class SubscriptionType(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"

class SellerBase(BaseModel):
    name: str
    description: Optional[str] = None
    banner_url: Optional[str] = None
    subscription_type: Optional[SubscriptionType] = None
    rating: Optional[float] = 0.0
    total_reviews: Optional[int] = 0
    is_active: Optional[bool] = True

class SellerCreate(SellerBase):
    pass

class SellerUpdate(SellerBase):
    pass

class SellerOut(SellerBase):
    id: int

    class Config:
        from_attributes = True  # Updated for Pydantic v2