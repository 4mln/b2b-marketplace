# plugins/seller/schemas.py
from pydantic import BaseModel
from typing import Optional

class SellerBase(BaseModel):
    name: str
    description: Optional[str] = None
    banner_url: Optional[str] = None
    subscription_type: Optional[str] = None
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
        orm_mode = True