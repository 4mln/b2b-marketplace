from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy import select, func
from datetime import datetime

from app.core.db import get_session
from plugins.seller.schemas import (
    SellerCreate,
    SellerUpdate,
    SellerOut,
    SubscriptionType,
    StorefrontOut,
    StorePolicyUpdate,
    StoreAnalytics,
)
from plugins.seller.crud import (
    create_seller,
    get_seller,
    update_seller,
    delete_seller,
    list_sellers,
    get_seller_by_user_id,
    update_store_policies,
    get_store_analytics,
)
from plugins.user.security import get_current_user
from plugins.user.models import User
from plugins.products.crud import list_products
from plugins.auth.models import User as AuthUser
from plugins.ratings.models import Rating
from plugins.products.models import Product

router = APIRouter()

# -----------------------------
# Create Seller
# -----------------------------
@router.post("/", response_model=SellerOut, operation_id="seller_create")
async def create_seller_endpoint(
    seller: SellerCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> SellerOut:
    return await create_seller(db, seller, user.id)

# -----------------------------
# Get Seller by ID
# -----------------------------
@router.get("/{seller_id}", response_model=SellerOut, operation_id="seller_get_by_id")
async def get_seller_endpoint(
    seller_id: int,
    db: AsyncSession = Depends(get_session),
) -> SellerOut:
    db_seller = await get_seller(db, seller_id)
    if not db_seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    return db_seller

# -----------------------------
# Update Seller
# -----------------------------
@router.put("/{seller_id}", response_model=SellerOut, operation_id="seller_update")
async def update_seller_endpoint(
    seller_id: int,
    seller_data: SellerUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> SellerOut:
    db_seller = await update_seller(db, seller_id, seller_data, user.id)
    if not db_seller:
        raise HTTPException(status_code=404, detail="Seller not found or permission denied")
    return db_seller

# -----------------------------
# Delete Seller
# -----------------------------
@router.delete("/{seller_id}", response_model=dict, operation_id="seller_delete")
async def delete_seller_endpoint(
    seller_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> dict:
    success = await delete_seller(db, seller_id, user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Seller not found or permission denied")
    return {"detail": "Seller deleted successfully"}

# -----------------------------
# List / Search Sellers
# -----------------------------
@router.get("/", response_model=List[SellerOut], operation_id="seller_list")
async def list_sellers_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Results per page"),
    sort_by: str = Query("id", description="Field to sort by"),
    sort_dir: str = Query("asc", regex="^(asc|desc)$", description="Sort direction"),
    search: Optional[str] = Query(None, description="Search term for seller name"),
    subscription_type: Optional[SubscriptionType] = Query(None, description="Filter by subscription type"),
    db: AsyncSession = Depends(get_session),
) -> List[SellerOut]:
    return await list_sellers(db, offset=(page-1)*page_size, limit=page_size)

# -----------------------------
# Enhanced Public Storefront
# -----------------------------
@router.get("/{seller_id}/storefront", response_model=StorefrontOut, operation_id="seller_storefront")
async def seller_storefront(
    seller_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    category: Optional[str] = Query(None, description="Filter by product category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    sort_by: str = Query("created_at", description="Sort products by: created_at, price, name, popularity"),
    sort_dir: str = Query("desc", regex="^(asc|desc)$", description="Sort direction"),
    db: AsyncSession = Depends(get_session),
    request: Request = None,
):
    # Get seller information
    seller = await get_seller(db, seller_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    # Get seller's user profile for KYC and business info
    owner = await db.get(AuthUser, seller.user_id)
    if not owner:
        raise HTTPException(status_code=404, detail="Seller profile not found")
    
    # Get seller's products with filters
    products = await list_products(
        db, 
        page=page, 
        page_size=page_size, 
        sort_by=sort_by, 
        sort_dir=sort_dir,
        seller_id=seller_id,
        min_price=min_price,
        max_price=max_price,
        category=category
    )
    
    # Filter only approved products
    approved_products = [p for p in products if getattr(p, "status", "approved") == "approved"]
    
    # Get seller ratings and reviews
    ratings_result = await db.execute(
        select(Rating)
        .where(Rating.ratee_id == seller.user_id)
        .order_by(Rating.created_at.desc())
        .limit(10)
    )
    ratings = ratings_result.scalars().all()
    
    # Calculate average rating
    avg_rating = 0
    total_ratings = 0
    if ratings:
        total_rating = sum((r.quality + r.timeliness + r.communication + r.reliability) / 4 for r in ratings)
        avg_rating = total_rating / len(ratings)
        total_ratings = len(ratings)
    
    # Get store analytics (basic metrics)
    total_products = await db.scalar(
        select(func.count(Product.id))
        .where(Product.seller_id == seller_id)
        .where(Product.status == "approved")
    )
    
    # Track storefront visit (for analytics)
    if request:
        # In a real implementation, you'd log this to analytics
        pass
    
    return StorefrontOut(
        seller=seller,
        owner_profile={
            "business_name": owner.business_name,
            "business_type": owner.business_type,
            "business_industry": owner.business_industry,
            "website": owner.website,
            "telegram_id": owner.telegram_id,
            "whatsapp_id": owner.whatsapp_id,
            "business_photo": owner.business_photo,
            "banner_photo": owner.banner_photo,
        },
        kyc_status=owner.kyc_status,
        products=approved_products,
        total_products=total_products or 0,
        average_rating=round(avg_rating, 2),
        total_ratings=total_ratings,
        recent_ratings=ratings[:5],  # Show last 5 ratings
        store_policies=seller.store_policies,
        seo_meta={
            "title": f"{owner.business_name or seller.name} - Store",
            "description": owner.business_description or f"Browse products from {owner.business_name or seller.name}",
            "keywords": f"{owner.business_industry}, {owner.business_name}, products, B2B",
        }
    )

# -----------------------------
# Get My Storefront (for seller)
# -----------------------------
@router.get("/me/storefront", response_model=StorefrontOut, operation_id="my_storefront")
async def my_storefront(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    seller = await get_seller_by_user_id(db, user.id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller profile not found")
    
    # Redirect to public storefront
    return await seller_storefront(seller.id, 1, 10, db=db)

# -----------------------------
# Update Store Policies
# -----------------------------
@router.patch("/me/storefront/policies", operation_id="update_store_policies")
async def update_store_policies_endpoint(
    policies: StorePolicyUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    seller = await get_seller_by_user_id(db, user.id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller profile not found")
    
    updated_seller = await update_store_policies(db, seller.id, policies)
    return {"detail": "Store policies updated successfully", "seller": updated_seller}

# -----------------------------
# Get Store Analytics
# -----------------------------
@router.get("/me/storefront/analytics", response_model=StoreAnalytics, operation_id="store_analytics")
async def store_analytics(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
):
    seller = await get_seller_by_user_id(db, user.id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller profile not found")
    
    analytics = await get_store_analytics(db, seller.id, days)
    return analytics

# -----------------------------
# Storefront SEO endpoint
# -----------------------------
@router.get("/{seller_id}/storefront/seo", operation_id="storefront_seo")
async def storefront_seo(
    seller_id: int,
    db: AsyncSession = Depends(get_session),
):
    """Get SEO metadata for storefront"""
    seller = await get_seller(db, seller_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    owner = await db.get(AuthUser, seller.user_id)
    if not owner:
        raise HTTPException(status_code=404, detail="Seller profile not found")
    
    # Get total products for SEO
    total_products = await db.scalar(
        select(func.count(Product.id))
        .where(Product.seller_id == seller_id)
        .where(Product.status == "approved")
    )
    
    return {
        "title": f"{owner.business_name or seller.name} - B2B Store",
        "description": owner.business_description or f"Browse {total_products or 0} products from {owner.business_name or seller.name}",
        "keywords": f"{owner.business_industry}, {owner.business_name}, B2B marketplace, wholesale",
        "og_title": f"{owner.business_name or seller.name} Store",
        "og_description": f"Professional B2B store with {total_products or 0} products",
        "og_image": owner.banner_photo or owner.business_photo,
        "canonical_url": f"/sellers/{seller_id}/storefront",
        "structured_data": {
            "@context": "https://schema.org",
            "@type": "Store",
            "name": owner.business_name or seller.name,
            "description": owner.business_description,
            "url": f"/sellers/{seller_id}/storefront",
            "telephone": owner.business_phones[0] if owner.business_phones else None,
            "email": owner.business_emails[0] if owner.business_emails else None,
            "address": {
                "@type": "PostalAddress",
                "addressCountry": "IR",
                "addressLocality": owner.business_addresses[0]["city"] if owner.business_addresses else None,
            } if owner.business_addresses else None,
        }
    }
