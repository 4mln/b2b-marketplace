"""
Enhanced Advertising System Schemas
Advanced targeting, bidding, and analytics capabilities
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class AdType(str, Enum):
    BANNER = "banner"
    POPUP = "popup"
    SIDEBAR = "sidebar"
    IN_FEED = "in_feed"
    SEARCH_RESULT = "search_result"
    PRODUCT_PAGE = "product_page"
    CATEGORY_PAGE = "category_page"
    HOMEPAGE = "homepage"


class AdStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    REJECTED = "rejected"
    EXPIRED = "expired"


class BiddingType(str, Enum):
    CPC = "cpc"
    CPM = "cpm"
    CPA = "cpa"
    FIXED = "fixed"


class TargetingType(str, Enum):
    LOCATION = "location"
    INTEREST = "interest"
    BEHAVIOR = "behavior"
    DEMOGRAPHIC = "demographic"
    DEVICE = "device"
    TIME = "time"
    KEYWORD = "keyword"


# Targeting Schemas
class LocationTargeting(BaseModel):
    countries: Optional[List[str]] = None
    cities: Optional[List[str]] = None
    regions: Optional[List[str]] = None
    postal_codes: Optional[List[str]] = None
    radius_km: Optional[float] = None


class DeviceTargeting(BaseModel):
    desktop: Optional[bool] = True
    mobile: Optional[bool] = True
    tablet: Optional[bool] = True
    browsers: Optional[List[str]] = None
    operating_systems: Optional[List[str]] = None


class TimeTargeting(BaseModel):
    days_of_week: Optional[List[int]] = None  # 0=Monday, 6=Sunday
    time_slots: Optional[List[Dict[str, str]]] = None  # [{"start": "09:00", "end": "17:00"}]
    timezone: Optional[str] = "Asia/Tehran"


class InterestTargeting(BaseModel):
    categories: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    behaviors: Optional[List[str]] = None


class DemographicTargeting(BaseModel):
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    gender: Optional[List[str]] = None
    income_level: Optional[List[str]] = None
    education_level: Optional[List[str]] = None


class TargetingConfig(BaseModel):
    location: Optional[LocationTargeting] = None
    device: Optional[DeviceTargeting] = None
    time: Optional[TimeTargeting] = None
    interest: Optional[InterestTargeting] = None
    demographic: Optional[DemographicTargeting] = None
    exclude_audiences: Optional[List[str]] = None


# Ad Schemas
class AdBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    ad_type: AdType
    image_url: Optional[str] = Field(None, max_length=500)
    video_url: Optional[str] = Field(None, max_length=500)
    landing_page_url: str = Field(..., max_length=500)
    
    # Targeting
    targeting_config: Optional[TargetingConfig] = None
    target_locations: Optional[Dict[str, Any]] = None
    target_keywords: Optional[List[str]] = None
    target_interests: Optional[List[str]] = None
    target_devices: Optional[List[str]] = None
    target_time_slots: Optional[List[Dict[str, str]]] = None
    
    # Budget and bidding
    bidding_type: BiddingType = BiddingType.CPC
    bid_amount: float = Field(..., gt=0)
    daily_budget: Optional[float] = Field(None, gt=0)
    total_budget: Optional[float] = Field(None, gt=0)
    start_date: datetime
    end_date: Optional[datetime] = None


class AdCreate(AdBase):
    pass


class AdUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)
    video_url: Optional[str] = Field(None, max_length=500)
    landing_page_url: Optional[str] = Field(None, max_length=500)
    targeting_config: Optional[TargetingConfig] = None
    bid_amount: Optional[float] = Field(None, gt=0)
    daily_budget: Optional[float] = Field(None, gt=0)
    total_budget: Optional[float] = Field(None, gt=0)
    end_date: Optional[datetime] = None
    status: Optional[AdStatus] = None


class AdOut(AdBase):
    id: int
    seller_id: int
    status: AdStatus
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    spend: float = 0.0
    ctr: float = 0.0
    cpc: float = 0.0
    cpm: float = 0.0
    is_priority: bool = False
    priority_score: float = 0.0
    quality_score: float = 0.0
    approval_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime] = None
    last_served_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Campaign Schemas
class AdCampaignBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    objective: str = Field(..., max_length=100)
    target_audience: Optional[Dict[str, Any]] = None
    budget_type: str = "daily"
    daily_budget: Optional[float] = Field(None, gt=0)
    total_budget: Optional[float] = Field(None, gt=0)
    start_date: datetime
    end_date: Optional[datetime] = None


class AdCampaignCreate(AdCampaignBase):
    pass


class AdCampaignUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    objective: Optional[str] = Field(None, max_length=100)
    target_audience: Optional[Dict[str, Any]] = None
    budget_type: Optional[str] = None
    daily_budget: Optional[float] = Field(None, gt=0)
    total_budget: Optional[float] = Field(None, gt=0)
    end_date: Optional[datetime] = None
    status: Optional[AdStatus] = None


class AdCampaignOut(AdCampaignBase):
    id: int
    seller_id: int
    status: AdStatus
    total_impressions: int = 0
    total_clicks: int = 0
    total_conversions: int = 0
    total_spend: float = 0.0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Analytics Schemas
class AdAnalyticsBase(BaseModel):
    date: datetime
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    spend: float = 0.0
    ctr: float = 0.0
    cpc: float = 0.0
    cpm: float = 0.0
    conversion_rate: float = 0.0
    unique_users: int = 0
    new_users: int = 0
    returning_users: int = 0
    desktop_impressions: int = 0
    mobile_impressions: int = 0
    tablet_impressions: int = 0
    country_breakdown: Optional[Dict[str, int]] = None
    city_breakdown: Optional[Dict[str, int]] = None


class AdAnalyticsOut(AdAnalyticsBase):
    id: int
    ad_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Impression and Click Schemas
class AdImpressionBase(BaseModel):
    page_url: Optional[str] = Field(None, max_length=500)
    referrer_url: Optional[str] = Field(None, max_length=500)
    user_agent: Optional[str] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    device_type: Optional[str] = Field(None, max_length=50)
    browser: Optional[str] = Field(None, max_length=100)
    os: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)


class AdImpressionCreate(AdImpressionBase):
    ad_id: int
    user_id: Optional[int] = None
    session_id: Optional[str] = Field(None, max_length=255)


class AdImpressionOut(AdImpressionBase):
    id: int
    ad_id: int
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AdClickBase(BaseModel):
    click_position: Optional[Dict[str, int]] = None
    page_url: Optional[str] = Field(None, max_length=500)
    referrer_url: Optional[str] = Field(None, max_length=500)
    user_agent: Optional[str] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    device_type: Optional[str] = Field(None, max_length=50)
    browser: Optional[str] = Field(None, max_length=100)
    os: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)


class AdClickCreate(AdClickBase):
    ad_id: int
    impression_id: Optional[int] = None
    user_id: Optional[int] = None
    session_id: Optional[str] = Field(None, max_length=255)


class AdClickOut(AdClickBase):
    id: int
    ad_id: int
    impression_id: Optional[int] = None
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Conversion Schemas
class AdConversionBase(BaseModel):
    conversion_type: str = Field(..., max_length=100)
    conversion_value: Optional[float] = None
    order_id: Optional[int] = None


class AdConversionCreate(AdConversionBase):
    ad_id: int
    click_id: Optional[int] = None
    user_id: Optional[int] = None


class AdConversionOut(AdConversionBase):
    id: int
    ad_id: int
    click_id: Optional[int] = None
    user_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Bidding Schemas
class AdBidBase(BaseModel):
    bid_amount: float = Field(..., gt=0)
    bid_type: BiddingType
    quality_score: float = Field(0.0, ge=0, le=10)
    final_score: float = Field(0.0, ge=0)
    won: bool = False
    winning_bid: Optional[float] = None
    position: Optional[int] = None


class AdBidCreate(AdBidBase):
    ad_id: int
    auction_id: str = Field(..., max_length=255)


class AdBidOut(AdBidBase):
    id: int
    ad_id: int
    auction_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Ad Space Schemas
class AdSpaceBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    ad_type: AdType
    width: Optional[int] = None
    height: Optional[int] = None
    max_file_size: Optional[int] = None
    allowed_formats: Optional[List[str]] = None
    page_type: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    targeting_rules: Optional[Dict[str, Any]] = None
    base_price: Optional[float] = None
    min_bid: Optional[float] = None
    reserve_price: Optional[float] = None
    is_active: bool = True


class AdSpaceCreate(AdSpaceBase):
    pass


class AdSpaceUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    max_file_size: Optional[int] = None
    allowed_formats: Optional[List[str]] = None
    page_type: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    targeting_rules: Optional[Dict[str, Any]] = None
    base_price: Optional[float] = None
    min_bid: Optional[float] = None
    reserve_price: Optional[float] = None
    is_active: Optional[bool] = None


class AdSpaceOut(AdSpaceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Blocklist Schemas
class AdBlocklistBase(BaseModel):
    domain: Optional[str] = Field(None, max_length=255)
    url_pattern: Optional[str] = Field(None, max_length=500)
    reason: str
    block_type: str = Field(..., max_length=50)
    is_active: bool = True


class AdBlocklistCreate(AdBlocklistBase):
    seller_id: Optional[int] = None


class AdBlocklistUpdate(BaseModel):
    domain: Optional[str] = Field(None, max_length=255)
    url_pattern: Optional[str] = Field(None, max_length=500)
    reason: Optional[str] = None
    is_active: Optional[bool] = None


class AdBlocklistOut(AdBlocklistBase):
    id: int
    seller_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Response Schemas
class AdListResponse(BaseModel):
    ads: List[AdOut]
    total: int
    page: int
    page_size: int


class AdCampaignListResponse(BaseModel):
    campaigns: List[AdCampaignOut]
    total: int
    page: int
    page_size: int


class AdAnalyticsListResponse(BaseModel):
    analytics: List[AdAnalyticsOut]
    total: int
    page: int
    page_size: int


class AdSpaceListResponse(BaseModel):
    ad_spaces: List[AdSpaceOut]
    total: int


class AdBlocklistListResponse(BaseModel):
    blocklist: List[AdBlocklistOut]
    total: int
    page: int
    page_size: int


# Performance Summary
class AdPerformanceSummary(BaseModel):
    ad_id: int
    total_impressions: int
    total_clicks: int
    total_conversions: int
    total_spend: float
    avg_ctr: float
    avg_cpc: float
    avg_cpm: float
    conversion_rate: float
    roi: float  # Return on investment


class CampaignPerformanceSummary(BaseModel):
    campaign_id: int
    total_ads: int
    active_ads: int
    total_impressions: int
    total_clicks: int
    total_conversions: int
    total_spend: float
    avg_ctr: float
    avg_cpc: float
    conversion_rate: float


# Targeting Validation
class TargetingValidation(BaseModel):
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    estimated_reach: Optional[int] = None
    estimated_cost: Optional[float] = None


# Auction Schemas
class AuctionRequest(BaseModel):
    ad_space_id: int
    user_context: Dict[str, Any]
    max_bids: int = 10


class AuctionResponse(BaseModel):
    auction_id: str
    winning_ad_id: Optional[int] = None
    winning_bid: Optional[float] = None
    ad_data: Optional[Dict[str, Any]] = None
    all_bids: List[AdBidOut] = []


# Budget and Billing
class BudgetSummary(BaseModel):
    daily_budget: float
    total_budget: float
    spent_today: float
    spent_total: float
    remaining_daily: float
    remaining_total: float
    budget_utilization: float  # Percentage


class BillingSummary(BaseModel):
    current_month_spend: float
    previous_month_spend: float
    outstanding_balance: float
    payment_method: Optional[str] = None
    next_billing_date: Optional[datetime] = None












