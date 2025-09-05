from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from plugins.orders.schemas import OrderCreate, OrderUpdate, OrderOut
from plugins.orders.crud import create_order, get_order, update_order, delete_order, list_orders

from plugins.user.models import User
from plugins.user.security import get_current_user
from plugins.products.dependencies import enforce_product_limit
from app.core.openapi import enhance_endpoint_docs
from plugins.orders.docs import order_docs

router = APIRouter()


@router.post("/", response_model=OrderOut, operation_id="order_create")
async def create_order_endpoint(
    order: OrderCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(__import__("app.db.session", fromlist=["get_session"]).get_session),
    _: None = Depends(enforce_product_limit)
):
    try:
        return await create_order(db, order, buyer_id=user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{order_id}", response_model=OrderOut, operation_id="order_get_by_id")
async def get_order_endpoint(order_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(__import__("app.db.session", fromlist=["get_session"]).get_session)):
    db_order = await get_order(db, order_id, buyer_id=user.id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order


@router.put("/{order_id}", response_model=OrderOut, operation_id="order_update")
async def update_order_endpoint(
    order_id: int,
    order_data: OrderUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(__import__("app.db.session", fromlist=["get_session"]).get_session),
):
    try:
        db_order = await update_order(db, order_id, order_data, buyer_id=user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order


@router.delete("/{order_id}", response_model=dict, operation_id="order_delete")
async def delete_order_endpoint(order_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(__import__("app.db.session", fromlist=["get_session"]).get_session)):
    success = await delete_order(db, order_id, buyer_id=user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"detail": "Order deleted successfully"}


@router.get("/", response_model=List[OrderOut], operation_id="order_list")
async def list_orders_endpoint(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(__import__("app.db.session", fromlist=["get_session"]).get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    return await list_orders(db, buyer_id=user.id, skip=skip, limit=limit)


# Apply OpenAPI documentation enhancements
enhance_endpoint_docs(router, order_docs)