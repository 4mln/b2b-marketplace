"""
Enhanced Advertising System CRUD Operations
Advanced targeting, bidding, and analytics capabilities
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import uuid
import json

from .models import (
    Ad, AdCampaign, AdImpression, AdClick, AdConversion, AdBid,
    AdSpace, AdBlocklist, AdAnalytics, AdStatus, AdType, BiddingType
)
from .schemas import (
    AdCreate, AdUpdate, AdCampaignCreate, AdCampaignUpdate,
    AdImpressionCreate, AdClickCreate, AdConversionCreate,
    AdBidCreate, AdSpaceCreate, AdSpaceUpdate, AdBlocklistCreate,
    TargetingConfig, TargetingValidation, AuctionRequest, AuctionResponse
)


# Ad CRUD Operations
def create_ad(db: Session, ad_data: AdCreate, seller_id: int) -> Ad:
    """Create a new advertisement"""
    db_ad = Ad(
        seller_id=seller_id,
        title=ad_data.title,
        description=ad_data.description,
        ad_type=ad_data.ad_type,
        image_url=ad_data.image_url,
        video_url=ad_data.video_url,
        landing_page_url=ad_data.landing_page_url,
        targeting_config=ad_data.targeting_config.dict() if ad_data.targeting_config else None,
        target_locations=ad_data.target_locations,
        target_keywords=ad_data.target_keywords,
        target_interests=ad_data.target_interests,
        target_devices=ad_data.target_devices,
        target_time_slots=ad_data.target_time_slots,
        bidding_type=ad_data.bidding_type,
        bid_amount=ad_data.bid_amount,
        daily_budget=ad_data.daily_budget,
        total_budget=ad_data.total_budget,
        start_date=ad_data.start_date,
        end_date=ad_data.end_date,
        status=AdStatus.DRAFT
    )
    db.add(db_ad)
    db.commit()
    db.refresh(db_ad)
    return db_ad


def get_ad(db: Session, ad_id: int) -> Optional[Ad]:
    """Get advertisement by ID"""
    return db.query(Ad).filter(Ad.id == ad_id).first()


def get_seller_ads(
    db: Session, 
    seller_id: int, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[AdStatus] = None,
    ad_type: Optional[AdType] = None
) -> Tuple[List[Ad], int]:
    """Get advertisements for a seller with filtering"""
    query = db.query(Ad).filter(Ad.seller_id == seller_id)
    
    if status:
        query = query.filter(Ad.status == status)
    if ad_type:
        query = query.filter(Ad.ad_type == ad_type)
    
    total = query.count()
    ads = query.offset(skip).limit(limit).all()
    
    return ads, total


def update_ad(db: Session, ad_id: int, ad_data: AdUpdate) -> Optional[Ad]:
    """Update advertisement"""
    db_ad = get_ad(db, ad_id)
    if not db_ad:
        return None
    
    update_data = ad_data.dict(exclude_unset=True)
    
    # Handle targeting config separately
    if ad_data.targeting_config:
        update_data["targeting_config"] = ad_data.targeting_config.dict()
    
    for field, value in update_data.items():
        setattr(db_ad, field, value)
    
    db_ad.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_ad)
    return db_ad


def delete_ad(db: Session, ad_id: int) -> bool:
    """Delete advertisement"""
    db_ad = get_ad(db, ad_id)
    if not db_ad:
        return False
    
    db.delete(db_ad)
    db.commit()
    return True


def approve_ad(db: Session, ad_id: int, admin_id: int, notes: Optional[str] = None) -> Optional[Ad]:
    """Approve advertisement"""
    db_ad = get_ad(db, ad_id)
    if not db_ad:
        return None
    
    db_ad.status = AdStatus.ACTIVE
    db_ad.approved_at = datetime.utcnow()
    db_ad.approval_notes = notes
    db_ad.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_ad)
    return db_ad


def reject_ad(db: Session, ad_id: int, admin_id: int, reason: str) -> Optional[Ad]:
    """Reject advertisement"""
    db_ad = get_ad(db, ad_id)
    if not db_ad:
        return None
    
    db_ad.status = AdStatus.REJECTED
    db_ad.rejection_reason = reason
    db_ad.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_ad)
    return db_ad


# Campaign CRUD Operations
def create_campaign(db: Session, campaign_data: AdCampaignCreate, seller_id: int) -> AdCampaign:
    """Create a new ad campaign"""
    db_campaign = AdCampaign(
        seller_id=seller_id,
        name=campaign_data.name,
        description=campaign_data.description,
        objective=campaign_data.objective,
        target_audience=campaign_data.target_audience,
        budget_type=campaign_data.budget_type,
        daily_budget=campaign_data.daily_budget,
        total_budget=campaign_data.total_budget,
        start_date=campaign_data.start_date,
        end_date=campaign_data.end_date,
        status=AdStatus.DRAFT
    )
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign


def get_campaign(db: Session, campaign_id: int) -> Optional[AdCampaign]:
    """Get campaign by ID"""
    return db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()


def get_seller_campaigns(
    db: Session, 
    seller_id: int, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[AdStatus] = None
) -> Tuple[List[AdCampaign], int]:
    """Get campaigns for a seller"""
    query = db.query(AdCampaign).filter(AdCampaign.seller_id == seller_id)
    
    if status:
        query = query.filter(AdCampaign.status == status)
    
    total = query.count()
    campaigns = query.offset(skip).limit(limit).all()
    
    return campaigns, total


def update_campaign(db: Session, campaign_id: int, campaign_data: AdCampaignUpdate) -> Optional[AdCampaign]:
    """Update campaign"""
    db_campaign = get_campaign(db, campaign_id)
    if not db_campaign:
        return None
    
    update_data = campaign_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_campaign, field, value)
    
    db_campaign.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_campaign)
    return db_campaign


# Impression and Click Tracking
def record_impression(
    db: Session, 
    ad_id: int, 
    user_id: Optional[int] = None,
    session_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> AdImpression:
    """Record an ad impression"""
    # Update ad impression count
    db_ad = get_ad(db, ad_id)
    if db_ad:
        db_ad.impressions += 1
        db_ad.last_served_at = datetime.utcnow()
        db.commit()
    
    # Create impression record
    db_impression = AdImpression(
        ad_id=ad_id,
        user_id=user_id,
        session_id=session_id,
        page_url=context.get("page_url") if context else None,
        referrer_url=context.get("referrer_url") if context else None,
        user_agent=context.get("user_agent") if context else None,
        ip_address=context.get("ip_address") if context else None,
        device_type=context.get("device_type") if context else None,
        browser=context.get("browser") if context else None,
        os=context.get("os") if context else None,
        country=context.get("country") if context else None,
        city=context.get("city") if context else None
    )
    
    db.add(db_impression)
    db.commit()
    db.refresh(db_impression)
    return db_impression


def record_click(
    db: Session, 
    ad_id: int, 
    impression_id: Optional[int] = None,
    user_id: Optional[int] = None,
    session_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> AdClick:
    """Record an ad click"""
    # Update ad click count and calculate CTR
    db_ad = get_ad(db, ad_id)
    if db_ad:
        db_ad.clicks += 1
        if db_ad.impressions > 0:
            db_ad.ctr = (db_ad.clicks / db_ad.impressions) * 100
        db.commit()
    
    # Create click record
    db_click = AdClick(
        ad_id=ad_id,
        impression_id=impression_id,
        user_id=user_id,
        session_id=session_id,
        click_position=context.get("click_position") if context else None,
        page_url=context.get("page_url") if context else None,
        referrer_url=context.get("referrer_url") if context else None,
        user_agent=context.get("user_agent") if context else None,
        ip_address=context.get("ip_address") if context else None,
        device_type=context.get("device_type") if context else None,
        browser=context.get("browser") if context else None,
        os=context.get("os") if context else None,
        country=context.get("country") if context else None,
        city=context.get("city") if context else None
    )
    
    db.add(db_click)
    db.commit()
    db.refresh(db_click)
    return db_click


def record_conversion(
    db: Session, 
    ad_id: int, 
    conversion_type: str,
    click_id: Optional[int] = None,
    user_id: Optional[int] = None,
    conversion_value: Optional[float] = None,
    order_id: Optional[int] = None
) -> AdConversion:
    """Record an ad conversion"""
    # Update ad conversion count
    db_ad = get_ad(db, ad_id)
    if db_ad:
        db_ad.conversions += 1
        db.commit()
    
    # Create conversion record
    db_conversion = AdConversion(
        ad_id=ad_id,
        click_id=click_id,
        user_id=user_id,
        conversion_type=conversion_type,
        conversion_value=conversion_value,
        order_id=order_id
    )
    
    db.add(db_conversion)
    db.commit()
    db.refresh(db_conversion)
    return db_conversion


# Analytics and Reporting
def get_ad_analytics(
    db: Session, 
    ad_id: int, 
    start_date: datetime,
    end_date: datetime
) -> List[AdAnalytics]:
    """Get analytics for an ad in a date range"""
    return db.query(AdAnalytics).filter(
        AdAnalytics.ad_id == ad_id,
        AdAnalytics.date >= start_date,
        AdAnalytics.date <= end_date
    ).order_by(AdAnalytics.date).all()


def get_campaign_analytics(
    db: Session, 
    campaign_id: int, 
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """Get aggregated analytics for a campaign"""
    # Get all ads in the campaign
    ads = db.query(Ad).filter(Ad.campaign_id == campaign_id).all()
    ad_ids = [ad.id for ad in ads]
    
    if not ad_ids:
        return {}
    
    # Aggregate metrics
    total_impressions = db.query(func.sum(Ad.impressions)).filter(Ad.id.in_(ad_ids)).scalar() or 0
    total_clicks = db.query(func.sum(Ad.clicks)).filter(Ad.id.in_(ad_ids)).scalar() or 0
    total_conversions = db.query(func.sum(Ad.conversions)).filter(Ad.id.in_(ad_ids)).scalar() or 0
    total_spend = db.query(func.sum(Ad.spend)).filter(Ad.id.in_(ad_ids)).scalar() or 0.0
    
    # Calculate averages
    avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    avg_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
    conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
    
    return {
        "campaign_id": campaign_id,
        "total_ads": len(ads),
        "active_ads": len([ad for ad in ads if ad.status == AdStatus.ACTIVE]),
        "total_impressions": total_impressions,
        "total_clicks": total_clicks,
        "total_conversions": total_conversions,
        "total_spend": total_spend,
        "avg_ctr": avg_ctr,
        "avg_cpc": avg_cpc,
        "conversion_rate": conversion_rate
    }


def get_seller_ad_performance(
    db: Session, 
    seller_id: int, 
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """Get overall ad performance for a seller"""
    ads = db.query(Ad).filter(
        Ad.seller_id == seller_id,
        Ad.created_at >= start_date,
        Ad.created_at <= end_date
    ).all()
    
    if not ads:
        return {}
    
    total_impressions = sum(ad.impressions for ad in ads)
    total_clicks = sum(ad.clicks for ad in ads)
    total_conversions = sum(ad.conversions for ad in ads)
    total_spend = sum(ad.spend for ad in ads)
    
    return {
        "seller_id": seller_id,
        "total_ads": len(ads),
        "active_ads": len([ad for ad in ads if ad.status == AdStatus.ACTIVE]),
        "total_impressions": total_impressions,
        "total_clicks": total_clicks,
        "total_conversions": total_conversions,
        "total_spend": total_spend,
        "avg_ctr": (total_clicks / total_impressions * 100) if total_impressions > 0 else 0,
        "avg_cpc": (total_spend / total_clicks) if total_clicks > 0 else 0,
        "conversion_rate": (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
    }


# Targeting and Matching
def validate_targeting(targeting_config: TargetingConfig) -> TargetingValidation:
    """Validate targeting configuration"""
    errors = []
    warnings = []
    
    if targeting_config.location:
        if targeting_config.location.countries and len(targeting_config.location.countries) > 50:
            warnings.append("Too many countries specified (max 50)")
    
    if targeting_config.time:
        if targeting_config.time.days_of_week:
            for day in targeting_config.time.days_of_week:
                if day < 0 or day > 6:
                    errors.append("Invalid day of week (must be 0-6)")
    
    return TargetingValidation(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        estimated_reach=10000,  # Placeholder
        estimated_cost=100.0    # Placeholder
    )


def match_ads_to_user(
    db: Session, 
    user_context: Dict[str, Any],
    ad_space_id: int,
    limit: int = 10
) -> List[Ad]:
    """Match ads to user based on targeting"""
    # Get active ads for the ad space
    query = db.query(Ad).filter(
        Ad.status == AdStatus.ACTIVE,
        Ad.start_date <= datetime.utcnow(),
        or_(Ad.end_date.is_(None), Ad.end_date >= datetime.utcnow())
    )
    
    # Apply basic targeting filters
    if user_context.get("country"):
        query = query.filter(
            or_(
                Ad.target_locations.is_(None),
                func.jsonb_path_exists(Ad.target_locations, f'$.countries[*] ? (@ == "{user_context["country"]}")')
            )
        )
    
    if user_context.get("device_type"):
        query = query.filter(
            or_(
                Ad.target_devices.is_(None),
                func.jsonb_path_exists(Ad.target_devices, f'$[*] ? (@ == "{user_context["device_type"]}")')
            )
        )
    
    # Order by quality score and bid amount
    ads = query.order_by(desc(Ad.quality_score), desc(Ad.bid_amount)).limit(limit).all()
    
    return ads


# Auction System
def run_auction(
    db: Session, 
    auction_request: AuctionRequest
) -> AuctionResponse:
    """Run real-time auction for ad space"""
    auction_id = str(uuid.uuid4())
    
    # Get matching ads
    matching_ads = match_ads_to_user(db, auction_request.user_context, auction_request.ad_space_id)
    
    if not matching_ads:
        return AuctionResponse(auction_id=auction_id)
    
    # Calculate final scores and determine winner
    bids = []
    for ad in matching_ads:
        # Calculate quality score (simplified)
        quality_score = ad.quality_score or 5.0
        
        # Calculate final score (bid * quality_score)
        final_score = ad.bid_amount * quality_score
        
        bid = AdBid(
            ad_id=ad.id,
            auction_id=auction_id,
            bid_amount=ad.bid_amount,
            bid_type=ad.bidding_type,
            quality_score=quality_score,
            final_score=final_score
        )
        bids.append(bid)
    
    # Sort by final score
    bids.sort(key=lambda x: x.final_score, reverse=True)
    
    # Determine winner
    if bids:
        winning_bid = bids[0]
        winning_bid.won = True
        winning_bid.position = 1
        
        # Record the bid
        db.add(winning_bid)
        db.commit()
        
        # Get winning ad data
        winning_ad = get_ad(db, winning_bid.ad_id)
        ad_data = {
            "id": winning_ad.id,
            "title": winning_ad.title,
            "image_url": winning_ad.image_url,
            "landing_page_url": winning_ad.landing_page_url,
            "ad_type": winning_ad.ad_type.value
        } if winning_ad else None
        
        return AuctionResponse(
            auction_id=auction_id,
            winning_ad_id=winning_bid.ad_id,
            winning_bid=winning_bid.bid_amount,
            ad_data=ad_data,
            all_bids=[b for b in bids[:auction_request.max_bids]]
        )
    
    return AuctionResponse(auction_id=auction_id)


# Ad Space Management
def create_ad_space(db: Session, space_data: AdSpaceCreate) -> AdSpace:
    """Create a new ad space"""
    db_space = AdSpace(**space_data.dict())
    db.add(db_space)
    db.commit()
    db.refresh(db_space)
    return db_space


def get_ad_spaces(db: Session, skip: int = 0, limit: int = 100) -> Tuple[List[AdSpace], int]:
    """Get available ad spaces"""
    query = db.query(AdSpace).filter(AdSpace.is_active == True)
    total = query.count()
    spaces = query.offset(skip).limit(limit).all()
    return spaces, total


def update_ad_space(db: Session, space_id: int, space_data: AdSpaceUpdate) -> Optional[AdSpace]:
    """Update ad space"""
    db_space = db.query(AdSpace).filter(AdSpace.id == space_id).first()
    if not db_space:
        return None
    
    update_data = space_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_space, field, value)
    
    db_space.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_space)
    return db_space


# Blocklist Management
def add_to_blocklist(
    db: Session, 
    blocklist_data: AdBlocklistCreate
) -> AdBlocklist:
    """Add item to blocklist"""
    db_blocklist = AdBlocklist(**blocklist_data.dict())
    db.add(db_blocklist)
    db.commit()
    db.refresh(db_blocklist)
    return db_blocklist


def get_blocklist(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    block_type: Optional[str] = None
) -> Tuple[List[AdBlocklist], int]:
    """Get blocklist items"""
    query = db.query(AdBlocklist).filter(AdBlocklist.is_active == True)
    
    if block_type:
        query = query.filter(AdBlocklist.block_type == block_type)
    
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total


def remove_from_blocklist(db: Session, blocklist_id: int) -> bool:
    """Remove item from blocklist"""
    db_item = db.query(AdBlocklist).filter(AdBlocklist.id == blocklist_id).first()
    if not db_item:
        return False
    
    db_item.is_active = False
    db_item.updated_at = datetime.utcnow()
    db.commit()
    return True


# Budget Management
def check_budget_limits(db: Session, ad_id: int) -> Dict[str, Any]:
    """Check if ad has exceeded budget limits"""
    ad = get_ad(db, ad_id)
    if not ad:
        return {"error": "Ad not found"}
    
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    # Check daily budget
    daily_spend = 0
    if ad.daily_budget:
        # Calculate today's spend (simplified)
        daily_spend = ad.spend * 0.1  # Placeholder calculation
        
        if daily_spend >= ad.daily_budget:
            return {
                "daily_limit_exceeded": True,
                "daily_spend": daily_spend,
                "daily_budget": ad.daily_budget
            }
    
    # Check total budget
    if ad.total_budget and ad.spend >= ad.total_budget:
        return {
            "total_limit_exceeded": True,
            "total_spend": ad.spend,
            "total_budget": ad.total_budget
        }
    
    return {
        "daily_limit_exceeded": False,
        "total_limit_exceeded": False,
        "daily_spend": daily_spend,
        "total_spend": ad.spend
    }


# Quality Score Calculation
def calculate_quality_score(db: Session, ad_id: int) -> float:
    """Calculate quality score for an ad"""
    ad = get_ad(db, ad_id)
    if not ad:
        return 0.0
    
    # Base score
    score = 5.0
    
    # CTR factor
    if ad.impressions > 0:
        ctr = (ad.clicks / ad.impressions) * 100
        if ctr > 2.0:
            score += 2.0
        elif ctr > 1.0:
            score += 1.0
        elif ctr < 0.1:
            score -= 1.0
    
    # Conversion rate factor
    if ad.clicks > 0:
        conv_rate = (ad.conversions / ad.clicks) * 100
        if conv_rate > 5.0:
            score += 2.0
        elif conv_rate > 2.0:
            score += 1.0
        elif conv_rate < 0.5:
            score -= 1.0
    
    # Recency factor
    if ad.last_served_at:
        days_since_last_served = (datetime.utcnow() - ad.last_served_at).days
        if days_since_last_served > 30:
            score -= 1.0
    
    # Ensure score is within bounds
    return max(0.0, min(10.0, score))








