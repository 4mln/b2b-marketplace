"""
Enhanced Advertising System Routes
Advanced targeting, bidding, and analytics capabilities
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.db.session import get_db_sync  # Or get_db if async
from app.core.auth import get_current_user_sync as get_current_user
from plugins.auth.models import User
from plugins.seller.crud import get_seller_by_user_id
from . import crud, schemas
from .models import AdStatus, AdType, BiddingType

router = APIRouter(prefix="/ads", tags=["advertising"])


# Ad Management Routes
@router.post("/", response_model=schemas.AdOut)
def create_ad(
    ad_data: schemas.AdCreate,
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Create a new advertisement"""
    # Verify user is a seller
    seller = get_seller_by_user_id(db, current_user.id)
    if not seller:
        raise HTTPException(status_code=403, detail="Only sellers can create ads")
    
    # Validate targeting configuration
    if ad_data.targeting_config:
        validation = crud.validate_targeting(ad_data.targeting_config)
        if not validation.is_valid:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid targeting configuration: {', '.join(validation.errors)}"
            )
    
    return crud.create_ad(db, ad_data, seller.id)


@router.get("/", response_model=schemas.AdListResponse)
def get_my_ads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[AdStatus] = None,
    ad_type: Optional[AdType] = None,
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Get current user's advertisements"""
    seller = get_seller_by_user_id(db, current_user.id)
    if not seller:
        raise HTTPException(status_code=403, detail="Only sellers can view ads")
    
    ads, total = crud.get_seller_ads(db, seller.id, skip, limit, status, ad_type)
    return schemas.AdListResponse(
        ads=ads,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/{ad_id}", response_model=schemas.AdOut)
def get_ad(
    ad_id: int,
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Get advertisement by ID"""
    ad = crud.get_ad(db, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    
    # Verify ownership
    seller = get_seller_by_user_id(db, current_user.id)
    if not seller or ad.seller_id != seller.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return ad


@router.patch("/{ad_id}", response_model=schemas.AdOut)
def update_ad(
    ad_id: int,
    ad_data: schemas.AdUpdate,
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Update advertisement"""
    ad = crud.get_ad(db, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    
    # Verify ownership
    seller = get_seller_by_user_id(db, current_user.id)
    if not seller or ad.seller_id != seller.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Validate targeting configuration
    if ad_data.targeting_config:
        validation = crud.validate_targeting(ad_data.targeting_config)
        if not validation.is_valid:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid targeting configuration: {', '.join(validation.errors)}"
            )
    
    updated_ad = crud.update_ad(db, ad_id, ad_data)
    if not updated_ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    
    return updated_ad


@router.delete("/{ad_id}")
def delete_ad(
    ad_id: int,
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Delete advertisement"""
    ad = crud.get_ad(db, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    
    # Verify ownership
    seller = get_seller_by_user_id(db, current_user.id)
    if not seller or ad.seller_id != seller.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    success = crud.delete_ad(db, ad_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ad not found")
    
    return {"message": "Ad deleted successfully"}


# Campaign Management Routes
@router.post("/campaigns", response_model=schemas.AdCampaignOut)
def create_campaign(
    campaign_data: schemas.AdCampaignCreate,
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Create a new ad campaign"""
    seller = get_seller_by_user_id(db, current_user.id)
    if not seller:
        raise HTTPException(status_code=403, detail="Only sellers can create campaigns")
    
    return crud.create_campaign(db, campaign_data, seller.id)


@router.get("/campaigns", response_model=schemas.AdCampaignListResponse)
def get_my_campaigns(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[AdStatus] = None,
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Get current user's campaigns"""
    seller = get_seller_by_user_id(db, current_user.id)
    if not seller:
        raise HTTPException(status_code=403, detail="Only sellers can view campaigns")
    
    campaigns, total = crud.get_seller_campaigns(db, seller.id, skip, limit, status)
    return schemas.AdCampaignListResponse(
        campaigns=campaigns,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/campaigns/{campaign_id}", response_model=schemas.AdCampaignOut)
def get_campaign(
    campaign_id: int,
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Get campaign by ID"""
    campaign = crud.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Verify ownership
    seller = get_seller_by_user_id(db, current_user.id)
    if not seller or campaign.seller_id != seller.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return campaign


@router.patch("/campaigns/{campaign_id}", response_model=schemas.AdCampaignOut)
def update_campaign(
    campaign_id: int,
    campaign_data: schemas.AdCampaignUpdate,
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Update campaign"""
    campaign = crud.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Verify ownership
    seller = get_seller_by_user_id(db, current_user.id)
    if not seller or campaign.seller_id != seller.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    updated_campaign = crud.update_campaign(db, campaign_id, campaign_data)
    if not updated_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return updated_campaign


# Analytics Routes
@router.get("/{ad_id}/analytics", response_model=List[schemas.AdAnalyticsOut])
def get_ad_analytics(
    ad_id: int,
    start_date: datetime = Query(default_factory=lambda: datetime.utcnow() - timedelta(days=30)),
    end_date: datetime = Query(default_factory=lambda: datetime.utcnow()),
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Get analytics for an ad"""
    ad = crud.get_ad(db, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    
    # Verify ownership
    seller = get_seller_by_user_id(db, current_user.id)
    if not seller or ad.seller_id != seller.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return crud.get_ad_analytics(db, ad_id, start_date, end_date)


@router.get("/campaigns/{campaign_id}/analytics", response_model=schemas.CampaignPerformanceSummary)
def get_campaign_analytics(
    campaign_id: int,
    start_date: datetime = Query(default_factory=lambda: datetime.utcnow() - timedelta(days=30)),
    end_date: datetime = Query(default_factory=lambda: datetime.utcnow()),
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Get analytics for a campaign"""
    campaign = crud.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Verify ownership
    seller = get_seller_by_user_id(db, current_user.id)
    if not seller or campaign.seller_id != seller.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    analytics = crud.get_campaign_analytics(db, campaign_id, start_date, end_date)
    if not analytics:
        raise HTTPException(status_code=404, detail="Analytics not found")
    
    return schemas.CampaignPerformanceSummary(**analytics)


@router.get("/performance/summary", response_model=schemas.AdPerformanceSummary)
def get_ad_performance_summary(
    start_date: datetime = Query(default_factory=lambda: datetime.utcnow() - timedelta(days=30)),
    end_date: datetime = Query(default_factory=lambda: datetime.utcnow()),
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Get overall ad performance summary for seller"""
    seller = get_seller_by_user_id(db, current_user.id)
    if not seller:
        raise HTTPException(status_code=403, detail="Only sellers can view performance")
    
    performance = crud.get_seller_ad_performance(db, seller.id, start_date, end_date)
    if not performance:
        raise HTTPException(status_code=404, detail="Performance data not found")
    
    return schemas.AdPerformanceSummary(**performance)


# Targeting and Validation Routes
@router.post("/targeting/validate", response_model=schemas.TargetingValidation)
def validate_targeting_config(
    targeting_config: schemas.TargetingConfig,
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Validate targeting configuration"""
    return crud.validate_targeting(targeting_config)


# Auction and Ad Serving Routes
@router.post("/auction", response_model=schemas.AuctionResponse)
def run_auction(
    auction_request: schemas.AuctionRequest,
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync)
):
    """Run real-time auction for ad space"""
    return crud.run_auction(db, auction_request)


@router.post("/{ad_id}/impression")
def record_impression(
    ad_id: int,
    impression_data: schemas.AdImpressionCreate,
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync)
):
    """Record an ad impression"""
    ad = crud.get_ad(db, ad_id)
    if not ad or ad.status != AdStatus.ACTIVE:
        raise HTTPException(status_code=404, detail="Ad not found or not active")
    
    # Check budget limits
    budget_check = crud.check_budget_limits(db, ad_id)
    if budget_check.get("daily_limit_exceeded") or budget_check.get("total_limit_exceeded"):
        raise HTTPException(status_code=429, detail="Budget limit exceeded")
    
    impression = crud.record_impression(
        db, 
        ad_id, 
        impression_data.user_id,
        impression_data.session_id,
        {
            "page_url": impression_data.page_url,
            "referrer_url": impression_data.referrer_url,
            "user_agent": impression_data.user_agent,
            "ip_address": impression_data.ip_address,
            "device_type": impression_data.device_type,
            "browser": impression_data.browser,
            "os": impression_data.os,
            "country": impression_data.country,
            "city": impression_data.city
        }
    )
    
    return {"message": "Impression recorded", "impression_id": impression.id}


@router.post("/{ad_id}/click")
def record_click(
    ad_id: int,
    click_data: schemas.AdClickCreate,
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync)
):
    """Record an ad click"""
    ad = crud.get_ad(db, ad_id)
    if not ad or ad.status != AdStatus.ACTIVE:
        raise HTTPException(status_code=404, detail="Ad not found or not active")
    
    click = crud.record_click(
        db, 
        ad_id, 
        click_data.impression_id,
        click_data.user_id,
        click_data.session_id,
        {
            "click_position": click_data.click_position,
            "page_url": click_data.page_url,
            "referrer_url": click_data.referrer_url,
            "user_agent": click_data.user_agent,
            "ip_address": click_data.ip_address,
            "device_type": click_data.device_type,
            "browser": click_data.browser,
            "os": click_data.os,
            "country": click_data.country,
            "city": click_data.city
        }
    )
    
    return {"message": "Click recorded", "click_id": click.id}


@router.post("/{ad_id}/conversion")
def record_conversion(
    ad_id: int,
    conversion_data: schemas.AdConversionCreate,
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync)
):
    """Record an ad conversion"""
    ad = crud.get_ad(db, ad_id)
    if not ad or ad.status != AdStatus.ACTIVE:
        raise HTTPException(status_code=404, detail="Ad not found or not active")
    
    conversion = crud.record_conversion(
        db, 
        ad_id, 
        conversion_data.conversion_type,
        conversion_data.click_id,
        conversion_data.user_id,
        conversion_data.conversion_value,
        conversion_data.order_id
    )
    
    return {"message": "Conversion recorded", "conversion_id": conversion.id}


# Ad Space Management Routes (Admin only)
@router.post("/spaces", response_model=schemas.AdSpaceOut)
def create_ad_space(
    space_data: schemas.AdSpaceCreate,
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Create a new ad space (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return crud.create_ad_space(db, space_data)


@router.get("/spaces", response_model=schemas.AdSpaceListResponse)
def get_ad_spaces(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync)
):
    """Get available ad spaces"""
    spaces, total = crud.get_ad_spaces(db, skip, limit)
    return schemas.AdSpaceListResponse(
        ad_spaces=spaces,
        total=total
    )


@router.patch("/spaces/{space_id}", response_model=schemas.AdSpaceOut)
def update_ad_space(
    space_id: int,
    space_data: schemas.AdSpaceUpdate,
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Update ad space (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    updated_space = crud.update_ad_space(db, space_id, space_data)
    if not updated_space:
        raise HTTPException(status_code=404, detail="Ad space not found")
    
    return updated_space


# Blocklist Management Routes (Admin only)
@router.post("/blocklist", response_model=schemas.AdBlocklistOut)
def add_to_blocklist(
    blocklist_data: schemas.AdBlocklistCreate,
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Add item to blocklist (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return crud.add_to_blocklist(db, blocklist_data)


@router.get("/blocklist", response_model=schemas.AdBlocklistListResponse)
def get_blocklist(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    block_type: Optional[str] = None,
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Get blocklist items (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    items, total = crud.get_blocklist(db, skip, limit, block_type)
    return schemas.AdBlocklistListResponse(
        blocklist=items,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.delete("/blocklist/{blocklist_id}")
def remove_from_blocklist(
    blocklist_id: int,
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Remove item from blocklist (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    success = crud.remove_from_blocklist(db, blocklist_id)
    if not success:
        raise HTTPException(status_code=404, detail="Blocklist item not found")
    
    return {"message": "Item removed from blocklist"}


# Budget Management Routes
@router.get("/{ad_id}/budget", response_model=schemas.BudgetSummary)
def get_budget_summary(
    ad_id: int,
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Get budget summary for an ad"""
    ad = crud.get_ad(db, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    
    # Verify ownership
    seller = get_seller_by_user_id(db, current_user.id)
    if not seller or ad.seller_id != seller.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    budget_check = crud.check_budget_limits(db, ad_id)
    
    return schemas.BudgetSummary(
        daily_budget=ad.daily_budget or 0,
        total_budget=ad.total_budget or 0,
        spent_today=budget_check.get("daily_spend", 0),
        spent_total=budget_check.get("total_spend", 0),
        remaining_daily=(ad.daily_budget or 0) - budget_check.get("daily_spend", 0),
        remaining_total=(ad.total_budget or 0) - budget_check.get("total_spend", 0),
        budget_utilization=(
            (budget_check.get("total_spend", 0) / (ad.total_budget or 1)) * 100
        )
    )


# Quality Score Routes
@router.get("/{ad_id}/quality-score")
def get_quality_score(
    ad_id: int,
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Get quality score for an ad"""
    ad = crud.get_ad(db, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    
    # Verify ownership
    seller = get_seller_by_user_id(db, current_user.id)
    if not seller or ad.seller_id != seller.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    quality_score = crud.calculate_quality_score(db, ad_id)
    
    return {
        "ad_id": ad_id,
        "quality_score": quality_score,
        "factors": {
            "ctr": ad.ctr,
            "conversion_rate": (ad.conversions / ad.clicks * 100) if ad.clicks > 0 else 0,
            "recency": "Good" if not ad.last_served_at or (datetime.utcnow() - ad.last_served_at).days <= 7 else "Needs improvement"
        }
    }


# Admin Routes for Ad Approval
@router.post("/{ad_id}/approve", response_model=schemas.AdOut)
def approve_ad(
    ad_id: int,
    notes: Optional[str] = None,
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Approve an advertisement (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    approved_ad = crud.approve_ad(db, ad_id, current_user.id, notes)
    if not approved_ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    
    return approved_ad


@router.post("/{ad_id}/reject", response_model=schemas.AdOut)
def reject_ad(
    ad_id: int,
    reason: str,
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Reject an advertisement (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    rejected_ad = crud.reject_ad(db, ad_id, current_user.id, reason)
    if not rejected_ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    
    return rejected_ad


@router.get("/pending/approval", response_model=schemas.AdListResponse)
def get_pending_ads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Get ads pending approval (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get ads with pending status
    query = db.query(crud.Ad).filter(crud.Ad.status == AdStatus.PENDING)
    total = query.count()
    ads = query.offset(skip).limit(limit).all()
    
    return schemas.AdListResponse(
        ads=ads,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )






