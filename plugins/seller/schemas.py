from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class SubscriptionType(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"

class SellerBase(BaseModel):
    name: str
    subscription_type: SubscriptionType

class SellerCreate(SellerBase):
    user_id: int

class SellerUpdate(BaseModel):
    name: Optional[str] = None
    subscription_type: Optional[SubscriptionType] = None

class SellerOut(SellerBase):
    id: int
    user_id: int

    model_config = {"from_attributes": True}

SellerOut.model_rebuild()