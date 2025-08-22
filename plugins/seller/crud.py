# plugins/seller/routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, asc
from typing import List

from app.core.db import get_session
from .models import Seller
from .schemas import SellerCreate, SellerUpdate, SellerOut, SubscriptionType
from .crud import create_seller, get_seller, update_seller, delete_seller

router = APIRouter(prefix="/sellers", tags=["Sellers"])

# -----------------------------
# Create Seller
# -----------------------------
@router.post("/", response_model=SellerOut)
async def create_seller_endpoint(
    seller: SellerCreate, user_id: int, db: AsyncSession = Depends(get_session)
):
    return await create_seller(db, seller, user_id)

# -----------------------------
# Read Seller by ID
# -----------------------------
@router.get("/{seller_id}", response_model=SellerOut)
async def get_seller_endpoint(seller_id: int, db: AsyncSession = Depends(get_session)):
    db_seller = await get_seller(db, seller_id)
    if not db_seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    return db_seller

# -----------------------------
# Update Seller
# -----------------------------
@router.put("/{seller_id}", response_model=SellerOut)
async def update_seller_endpoint(
    seller_id: int,
    seller_data: SellerUpdate,
    user_id: int,
    db: AsyncSession = Depends(get_session),
):
    db_seller = await update_seller(db, seller_id, seller_data, user_id)
    if not db_seller:
        raise HTTPException(status_code=404, detail="Seller not found or permission denied")
    return db_seller

# -----------------------------
# Delete Seller
# -----------------------------
@router.delete("/{seller_id}", response_model=dict)
async def delete_seller_endpoint(seller_id: int, user_id: int, db: AsyncSession = Depends(get_session)):
    success = await delete_seller(db, seller_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Seller not found or permission denied")
    return {"detail": "Seller deleted successfully"}

# -----------------------------
# List all Sellers (pagination + sorting)
# -----------------------------
@router.get("/", response_model=List[SellerOut])
async def list_sellers_endpoint(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: str = Query("id"),
    sort_dir: str = Query("asc", regex="^(asc|desc)$"),
    db: AsyncSession = Depends(get_session)
):
    sort_column = getattr(Seller, sort_by, None)
    if not sort_column:
        raise HTTPException(status_code=400, detail=f"Invalid sort field: {sort_by}")
    order = asc(sort_column) if sort_dir == "asc" else desc(sort_column)
    result = await db.execute(
        select(Seller).order_by(order).offset((page - 1) * page_size).limit(page_size)
    )
    return result.scalars().all()

# -----------------------------
# Search Sellers by name or description
# -----------------------------
@router.get("/search", response_model=List[SellerOut])
async def search_sellers_endpoint(
    query: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: str = Query("id"),
    sort_dir: str = Query("asc", regex="^(asc|desc)$"),
    db: AsyncSession = Depends(get_session)
):
    sort_column = getattr(Seller, sort_by, None)
    if not sort_column:
        raise HTTPException(status_code=400, detail=f"Invalid sort field: {sort_by}")
    order = asc(sort_column) if sort_dir == "asc" else desc(sort_column)
    result = await db.execute(
        select(Seller)
        .where(
            Seller.name.ilike(f"%{query}%") | Seller.description.ilike(f"%{query}%")
        )
        .order_by(order)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return result.scalars().all()

# -----------------------------
# Get top-rated sellers
# -----------------------------
@router.get("/top/", response_model=List[SellerOut])
async def top_sellers(limit: int = 10, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Seller).order_by(desc(Seller.rating)).limit(limit))
    return result.scalars().all()

# -----------------------------
# Filter sellers by subscription type
# -----------------------------
@router.get("/subscription/{subscription_type}", response_model=List[SellerOut])
async def sellers_by_subscription(
    subscription_type: SubscriptionType, db: AsyncSession = Depends(get_session)
):
    result = await db.execute(
        select(Seller).where(Seller.subscription_type == subscription_type.value)
    )
    return result.scalars().all()

# -----------------------------
# Activate / Deactivate seller
# -----------------------------
@router.patch("/{seller_id}/activate", response_model=SellerOut)
async def activate_seller(
    seller_id: int, is_active: bool, user_id: int, db: AsyncSession = Depends(get_session)
):
    db_seller = await get_seller(db, seller_id)
    if not db_seller or db_seller.user_id != user_id:
        raise HTTPException(status_code=404, detail="Seller not found or permission denied")
    db_seller.is_active = is_active
    await db.commit()
    await db.refresh(db_seller)
    return db_seller