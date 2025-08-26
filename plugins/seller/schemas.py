from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

# -----------------------------
# Subscription Types
# -----------------------------
class SubscriptionType(str, Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    VIP = "vip"

# -----------------------------
# Seller Base
# -----------------------------
class SellerBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    subscription: Optional[SubscriptionType] = SubscriptionType.BASIC
    model_config = {"from_attributes": True}

# -----------------------------
# Seller Create
# -----------------------------
class SellerCreate(SellerBase):
    password: str
    model_config = {"from_attributes": True}

# -----------------------------
# Seller Update
# -----------------------------
class SellerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    subscription: Optional[SubscriptionType] = None
    model_config = {"from_attributes": True}

# -----------------------------
# Seller Output
# -----------------------------
class SellerOut(SellerBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

# -----------------------------
# List of Sellers
# -----------------------------
class SellerList(BaseModel):
    items: List[SellerOut]
    total: int
    model_config = {"from_attributes": True}

# -----------------------------
# Gamification / Leaderboard
# -----------------------------
class BadgeOut(BaseModel):
    name: str
    description: str
    icon_url: Optional[str] = None
    model_config = {"from_attributes": True}

class LeaderboardEntry(BaseModel):
    username: str
    score: int
    rank: Optional[int] = None
    model_config = {"from_attributes": True}

class GamificationProgress(BaseModel):
    user_id: int
    points: int = 0
    level: int = 1
    badges: List[str] = []
    achievements: Dict[str, bool] = {}
    last_updated: Optional[datetime] = None
    model_config = {"from_attributes": True}

class GamificationUpdate(BaseModel):
    points: Optional[int] = None
    level: Optional[int] = None
    badges: Optional[List[str]] = None
    achievements: Optional[Dict[str, bool]] = None
    model_config = {"from_attributes": True}

class GamificationCreate(BaseModel):
    user_id: int
    points: int = 0
    level: int = 1
    badges: List[str] = []
    achievements: Dict[str, bool] = {}
    model_config = {"from_attributes": True}

class GamificationList(BaseModel):
    items: List[GamificationProgress]
    total: int
    model_config = {"from_attributes": True}

class LeaderboardOut(BaseModel):
    leaderboard: List[LeaderboardEntry]
    model_config = {"from_attributes": True}
