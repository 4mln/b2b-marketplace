from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from plugins.orders.schemas import OrderCreate, OrderUpdate, OrderOut
from plugins.orders.crud import create_order, get_order, update_order, delete_order, list_orders
from app.core.db import get_session
from plugins.user.models import User
from plugins.user.security import get_current_user

router = APIRouter()

@router.post("/", response_model=OrderOut, operation_id="order_create")
async def create_order_endpoint(
    order: OrderCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    return await create_order(db, order)

@router.get("/{order_id}", response_model=OrderOut, operation_id="order_get_by_id")
async def get_order_endpoint(order_id: int, db: AsyncSession = Depends(get_session)):
    db_order = await get_order(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@router.put("/{order_id}", response_model=OrderOut, operation_id="order_update")
async def update_order_endpoint(
    order_id: int,
    order_data: OrderUpdate,
    db: AsyncSession = Depends(get_session),
):
    db_order = await update_order(db, order_id, order_data)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@router.delete("/{order_id}", response_model=dict, operation_id="order_delete")
async def delete_order_endpoint(order_id: int, db: AsyncSession = Depends(get_session)):
    success = await delete_order(db, order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"detail": "Order deleted successfully"}

@router.get("/", response_model=List[OrderOut], operation_id="order_list")
async def list_orders_endpoint(
    buyer_id: Optional[int] = None,
    seller_id: Optional[int] = None,
    db: AsyncSession = Depends(get_session),
):
    return await list_orders(db, buyer_id, seller_id)