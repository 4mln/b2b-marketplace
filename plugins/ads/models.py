"""
Enhanced Advertising System Models
Advanced targeting, bidding, and analytics capabilities
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.db.base import Base
# Ensure 'orders' table is registered before defining FKs to it
try:
    from plugins.orders.models import Order  # noqa: F401
except Exception:
    # Safe import guard; plugin load order should handle this, but ensure no import-time crash
    Order = None  # type: ignore


class AdType(str, enum.Enum):
    BANNER = "banner"
    POPUP = "popup"
    SIDEBAR = "sidebar"
    IN_FEED = "in_feed"
    SEARCH_RESULT = "search_result"
    PRODUCT_PAGE = "product_page"
    CATEGORY_PAGE = "category_page"
    HOMEPAGE = "homepage"


class AdStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    REJECTED = "rejected"
    EXPIRED = "expired"


class BiddingType(str, enum.Enum):
    CPC = "cpc"  # Cost per click
    CPM = "cpm"  # Cost per thousand impressions
    CPA = "cpa"  # Cost per action
    FIXED = "fixed"  # Fixed price


class TargetingType(str, enum.Enum):
    LOCATION = "location"
    INTEREST = "interest"
    BEHAVIOR = "behavior"
    DEMOGRAPHIC = "demographic"
    DEVICE = "device"
    TIME = "time"
    KEYWORD = "keyword"


class Ad(Base):
    """Enhanced advertisement model"""
    __tablename__ = "ads"
    
    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    title = Column(String(255), nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    description = Column(Text, nullable=True)
    ad_type = Column(Enum(AdType), nullable=False)
    status = Column(Enum(AdStatus), default=AdStatus.DRAFT)
    
    # Link to AdCampaign
    campaign_id = Column(Integer, ForeignKey("ad_campaigns.id"), nullable=True)
    campaign = relationship("AdCampaign", back_populates="ads")


    # Media content
    image_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    landing_page_url = Column(String(500), nullable=False)
    
    # Targeting
    targeting_config = Column(JSON, nullable=True)  # Advanced targeting rules
    target_locations = Column(JSON, nullable=True)  # Geographic targeting
    target_keywords = Column(JSON, nullable=True)  # Keyword targeting
    target_interests = Column(JSON, nullable=True)  # Interest targeting
    target_devices = Column(JSON, nullable=True)  # Device targeting
    target_time_slots = Column(JSON, nullable=True)  # Time-based targeting
    
    # Budget and bidding
    bidding_type = Column(Enum(BiddingType), default=BiddingType.CPC)
    bid_amount = Column(Float, nullable=False)
    daily_budget = Column(Float, nullable=True)
    total_budget = Column(Float, nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Performance tracking
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    ctr = Column(Float, default=0.0)  # Click-through rate
    cpc = Column(Float, default=0.0)  # Cost per click
    cpm = Column(Float, default=0.0)  # Cost per thousand impressions
    
    # Advanced features
    is_priority = Column(Boolean, default=False)
    priority_score = Column(Float, default=0.0)
    quality_score = Column(Float, default=0.0)
    approval_notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
    last_served_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    seller = relationship("Seller")
    impressions_log = relationship("AdImpression", back_populates="ad")
    clicks_log = relationship("AdClick", back_populates="ad")
    conversions_log = relationship("AdConversion", back_populates="ad")
    bids = relationship("AdBid", back_populates="ad")


class AdCampaign(Base):
    """Campaign management for ads"""
    __tablename__ = "ad_campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(AdStatus), default=AdStatus.DRAFT)
    
    # Campaign settings
    objective = Column(String(100), nullable=False)  # brand_awareness, traffic, conversions, etc.
    target_audience = Column(JSON, nullable=True)
    budget_type = Column(String(50), default="daily")  # daily, lifetime
    daily_budget = Column(Float, nullable=True)
    total_budget = Column(Float, nullable=True)
    
    # Campaign performance
    total_impressions = Column(Integer, default=0)
    total_clicks = Column(Integer, default=0)
    total_conversions = Column(Integer, default=0)
    total_spend = Column(Float, default=0.0)
    
    # Timestamps
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    seller = relationship("Seller")
    ads = relationship("Ad", back_populates="campaign")


class AdImpression(Base):
    """Track ad impressions"""
    __tablename__ = "ad_impressions"
    
    id = Column(Integer, primary_key=True, index=True)
    ad_id = Column(Integer, ForeignKey("ads.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(255), nullable=True)
    
    # Impression details
    page_url = Column(String(500), nullable=True)
    referrer_url = Column(String(500), nullable=True)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Device and location info
    device_type = Column(String(50), nullable=True)
    browser = Column(String(100), nullable=True)
    os = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ad = relationship("Ad", back_populates="impressions_log")
    user = relationship("User")


class AdClick(Base):
    """Track ad clicks"""
    __tablename__ = "ad_clicks"
    
    id = Column(Integer, primary_key=True, index=True)
    ad_id = Column(Integer, ForeignKey("ads.id"), nullable=False)
    impression_id = Column(Integer, ForeignKey("ad_impressions.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(255), nullable=True)
    
    # Click details
    click_position = Column(JSON, nullable=True)  # x, y coordinates
    page_url = Column(String(500), nullable=True)
    referrer_url = Column(String(500), nullable=True)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Device and location info
    device_type = Column(String(50), nullable=True)
    browser = Column(String(100), nullable=True)
    os = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ad = relationship("Ad", back_populates="clicks_log")
    impression = relationship("AdImpression")
    user = relationship("User")


class AdConversion(Base):
    """Track ad conversions"""
    __tablename__ = "ad_conversions"
    
    id = Column(Integer, primary_key=True, index=True)
    ad_id = Column(Integer, ForeignKey("ads.id"), nullable=False)
    click_id = Column(Integer, ForeignKey("ad_clicks.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Conversion details
    conversion_type = Column(String(100), nullable=False)  # purchase, signup, download, etc.
    conversion_value = Column(Float, nullable=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ad = relationship("Ad", back_populates="conversions_log")
    click = relationship("AdClick")
    user = relationship("User")
    order = relationship("Order")


class AdBid(Base):
    """Real-time bidding system"""
    __tablename__ = "ad_bids"
    
    id = Column(Integer, primary_key=True, index=True)
    ad_id = Column(Integer, ForeignKey("ads.id"), nullable=False)
    auction_id = Column(String(255), nullable=False)
    
    # Bid details
    bid_amount = Column(Float, nullable=False)
    bid_type = Column(Enum(BiddingType), nullable=False)
    quality_score = Column(Float, default=0.0)
    final_score = Column(Float, default=0.0)
    
    # Auction result
    won = Column(Boolean, default=False)
    winning_bid = Column(Float, nullable=True)
    position = Column(Integer, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ad = relationship("Ad", back_populates="bids")


class AdSpace(Base):
    """Available ad spaces on the platform"""
    __tablename__ = "ad_spaces"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    ad_type = Column(Enum(AdType), nullable=False)
    
    # Space specifications
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    max_file_size = Column(Integer, nullable=True)  # in KB
    allowed_formats = Column(JSON, nullable=True)  # ["jpg", "png", "gif"]
    
    # Location and targeting
    page_type = Column(String(100), nullable=True)  # homepage, category, product, etc.
    position = Column(String(100), nullable=True)  # top, sidebar, bottom, etc.
    targeting_rules = Column(JSON, nullable=True)
    
    # Pricing
    base_price = Column(Float, nullable=True)
    min_bid = Column(Float, nullable=True)
    reserve_price = Column(Float, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AdBlocklist(Base):
    """Blocklist for inappropriate ads"""
    __tablename__ = "ad_blocklist"
    
    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=True)
    domain = Column(String(255), nullable=True)
    url_pattern = Column(String(500), nullable=True)
    reason = Column(Text, nullable=False)
    
    # Blocklist details
    block_type = Column(String(50), nullable=False)  # domain, url, seller
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    seller = relationship("Seller")


class AdAnalytics(Base):
    """Aggregated ad analytics"""
    __tablename__ = "ad_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    ad_id = Column(Integer, ForeignKey("ads.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    
    # Daily metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    
    # Calculated metrics
    ctr = Column(Float, default=0.0)
    cpc = Column(Float, default=0.0)
    cpm = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)
    
    # Audience metrics
    unique_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    returning_users = Column(Integer, default=0)
    
    # Device breakdown
    desktop_impressions = Column(Integer, default=0)
    mobile_impressions = Column(Integer, default=0)
    tablet_impressions = Column(Integer, default=0)
    
    # Geographic breakdown
    country_breakdown = Column(JSON, nullable=True)
    city_breakdown = Column(JSON, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    ad = relationship("Ad")











