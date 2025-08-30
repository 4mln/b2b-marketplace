from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Optional, Any
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
# Store Policies
# -----------------------------
class StorePolicies(BaseModel):
    return_policy: Optional[str] = None
    shipping_policy: Optional[str] = None
    payment_policy: Optional[str] = None
    warranty_policy: Optional[str] = None
    minimum_order: Optional[float] = None
    lead_time_days: Optional[int] = None
    bulk_discount: Optional[bool] = False
    bulk_discount_threshold: Optional[int] = None
    bulk_discount_percentage: Optional[float] = None

class StorePolicyUpdate(BaseModel):
    return_policy: Optional[str] = None
    shipping_policy: Optional[str] = None
    payment_policy: Optional[str] = None
    warranty_policy: Optional[str] = None
    minimum_order: Optional[float] = Field(None, ge=0)
    lead_time_days: Optional[int] = Field(None, ge=0, le=365)
    bulk_discount: Optional[bool] = False
    bulk_discount_threshold: Optional[int] = Field(None, ge=1)
    bulk_discount_percentage: Optional[float] = Field(None, ge=0, le=100)

# -----------------------------
# Store Analytics
# -----------------------------
class StoreAnalytics(BaseModel):
    total_products: int
    total_orders: int
    total_revenue: float
    average_rating: float
    total_ratings: int
    store_visits: int
    unique_visitors: int
    conversion_rate: float
    top_products: List[Dict[str, Any]]
    recent_orders: List[Dict[str, Any]]
    revenue_trend: List[Dict[str, Any]]
    visitor_trend: List[Dict[str, Any]]

# -----------------------------
# SEO Metadata
# -----------------------------
class SEOMetadata(BaseModel):
    title: str
    description: str
    keywords: str
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    canonical_url: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None

# -----------------------------
# Storefront Output
# -----------------------------
class StorefrontOut(BaseModel):
    seller: Any  # SellerOut
    owner_profile: Dict[str, Any]
    kyc_status: str
    products: List[Any]  # List[ProductOut]
    total_products: int
    average_rating: float
    total_ratings: int
    recent_ratings: List[Any]  # List[RatingOut]
    store_policies: Optional[StorePolicies] = None
    seo_meta: SEOMetadata

# -----------------------------
# Seller Base
# -----------------------------
class SellerBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    subscription: Optional[SubscriptionType] = SubscriptionType.BASIC
    store_policies: Optional[StorePolicies] = None
    store_url: Optional[str] = None
    is_featured: bool = False
    is_verified: bool = False
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
    store_policies: Optional[StorePolicyUpdate] = None
    store_url: Optional[str] = None
    is_featured: Optional[bool] = None
    is_verified: Optional[bool] = None
    model_config = {"from_attributes": True}

# -----------------------------
# Seller Output
# -----------------------------
class SellerOut(SellerBase):
    id: int
    user_id: int
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
