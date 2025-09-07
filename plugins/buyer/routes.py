# plugins/buyer/routes.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from plugins.buyer.schemas import BuyerCreate, BuyerUpdate, BuyerOut
from plugins.buyer import crud
from plugins.user.security import get_current_user
from plugins.user.models import User

router = APIRouter(prefix="/api/v1/buyers", tags=["buyers"])


# -----------------------------
# Create Buyer
# -----------------------------
@router.post("/", response_model=BuyerOut)
async def create_new_buyer(
    buyer: BuyerCreate,
    db: AsyncSession = Depends(__import__("app.db.session", fromlist=["get_session"]).get_session),
    user: User = Depends(get_current_user),
):
    return await crud.create_buyer(db, buyer, user.id)


# -----------------------------
# Get Buyer by ID
# -----------------------------
@router.get("/{buyer_id}", response_model=BuyerOut)
async def read_buyer(
    buyer_id: int,
    db: AsyncSession = Depends(__import__("app.db.session", fromlist=["get_session"]).get_session),
):
    buyer = await crud.get_buyer(db, buyer_id)
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
    return buyer


# -----------------------------
# Update Buyer
# -----------------------------
@router.put("/{buyer_id}", response_model=BuyerOut)
async def update_buyer_endpoint(
    buyer_id: int,
    buyer_data: BuyerUpdate,
    db: AsyncSession = Depends(__import__("app.db.session", fromlist=["get_session"]).get_session),
    user: User = Depends(get_current_user),
):
    updated = await crud.update_buyer(db, buyer_id, buyer_data, user.id)
    if not updated:
        raise HTTPException(
            status_code=404, detail="Buyer not found or permission denied"
        )
    return updated


# -----------------------------
# Delete Buyer
# -----------------------------
@router.delete("/{buyer_id}", response_model=dict)
async def delete_buyer_endpoint(
    buyer_id: int,
    db: AsyncSession = Depends(__import__("app.db.session", fromlist=["get_session"]).get_session),
    user: User = Depends(get_current_user),
):
    success = await crud.delete_buyer(db, buyer_id, user.id)
    if not success:
        raise HTTPException(
            status_code=404, detail="Buyer not found or permission denied"
        )
    return {"detail": "Buyer deleted successfully"}


# -----------------------------
# List / Search Buyers
# -----------------------------
@router.get("/", response_model=List[BuyerOut])
async def list_buyers_endpoint(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: str = Query("id"),
    sort_dir: str = Query("asc", pattern="^(asc|desc)$"),
    search: Optional[str] = None,
    db: AsyncSession = Depends(__import__("app.db.session", fromlist=["get_session"]).get_session),
):
    return await crud.list_buyers(db, page, page_size, sort_by, sort_dir, search)