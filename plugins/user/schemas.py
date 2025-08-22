from __future__ import annotations
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from plugins.seller.schemas import SellerOut
from plugins.buyer.schemas import BuyerOut
from plugins.gamification.schemas import GamificationProgress

class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    password: Optional[str] = None

class UserOut(UserBase):
    id: int
    sellers: List[SellerOut] = []
    buyer: Optional[BuyerOut] = None
    gamification: Optional[GamificationProgress] = None

    model_config = {"from_attributes": True}

UserOut.model_rebuild()  # 🔹 fix forward refs