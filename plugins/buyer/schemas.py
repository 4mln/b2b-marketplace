from __future__ import annotations
from pydantic import BaseModel
from typing import Optional

class BuyerBase(BaseModel):
    full_name: str
    phone: Optional[str] = None
    address: Optional[str] = None

class BuyerCreate(BuyerBase):
    pass

class BuyerUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class BuyerOut(BuyerBase):
    id: int
    user_id: int
    user: Optional["UserOut"] = None  # 🔹 forward reference as string

    model_config = {"from_attributes": True}

# 🔹 rebuild to resolve forward references
BuyerOut.model_rebuild()