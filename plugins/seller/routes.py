from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.db import get_session
from plugins.seller.schemas import (
    SellerCreate,
    SellerUpdate,
    SellerOut,
    SubscriptionType,
)
from plugins.seller.crud import (
    create_seller,
    get_seller,
    update_seller,
    delete_seller,
    list_sellers,
)
from plugins.user.security import get_current_user
from plugins.user.models import User
from plugins.products.crud import list_products
from plugins.auth.models import User as AuthUser

router = APIRouter()

# -----------------------------
# Create Seller
# -----------------------------
@router.post("/", response_model=SellerOut, operation_id="seller_create")
async def create_seller_endpoint(
    seller: SellerCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session),
) -> SellerOut:
    return await create_seller(db, seller, user.id)

# -----------------------------
# Get Seller by ID
# -----------------------------
@router.get("/{seller_id}", response_model=SellerOut, operation_id="seller_get_by_id")
async def get_seller_endpoint(
    seller_id: int,
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session),
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
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session),
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
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session),
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
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session),
) -> List[SellerOut]:
    return await list_sellers(db, offset=(page-1)*page_size, limit=page_size)


# -----------------------------
# Public storefront
# -----------------------------
@router.get("/{seller_id}/storefront", operation_id="seller_storefront")
async def seller_storefront(
    seller_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session),
):
    seller = await get_seller(db, seller_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    products = await list_products(db, page=page, page_size=page_size, sort_by="id", sort_dir="desc", search=None)
    products = [p for p in products if getattr(p, "status", "approved") == "approved"]
    # KYC badge from auth User.kyc_status
    owner = await db.get(AuthUser, seller.user_id)
    kyc_badge = getattr(owner, "kyc_status", "pending") if owner else "pending"
    return {"seller": seller, "kyc_badge": kyc_badge, "products": products}
