from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session
from plugins.buyer.schemas import BuyerCreate, BuyerUpdate, BuyerOut
from plugins.buyer.crud import create_buyer, get_buyer, update_buyer, delete_buyer
from plugins.buyer.models import Buyer
from plugins.user.security import get_current_user
from plugins.user.models import User

router = APIRouter(prefix="/buyers", tags=["buyers"])

@router.post("/", response_model=BuyerOut)
async def create_buyer_route(
    buyer_in: BuyerCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await create_buyer(db, buyer_in, user_id=current_user.id)

@router.get("/{buyer_id}", response_model=BuyerOut)
async def get_buyer_route(
    buyer_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    buyer = await get_buyer(db, buyer_id)
    if not buyer or buyer.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Buyer not found")
    return buyer

@router.put("/{buyer_id}", response_model=BuyerOut)
async def update_buyer_route(
    buyer_id: int,
    buyer_in: BuyerUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    buyer = await get_buyer(db, buyer_id)
    if not buyer or buyer.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Buyer not found")
    return await update_buyer(db, buyer, buyer_in)

@router.delete("/{buyer_id}")
async def delete_buyer_route(
    buyer_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    buyer = await get_buyer(db, buyer_id)
    if not buyer or buyer.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Buyer not found")
    await delete_buyer(db, buyer)
    return {"ok": True}