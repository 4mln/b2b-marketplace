from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete
from plugins.orders.models import Order  # we will create this next
from typing import List, Optional
from plugins.orders.schemas import OrderCreate, OrderUpdate

async def create_order(db: AsyncSession, order: OrderCreate):
    db_order = Order(
        buyer_id=order.buyer_id,
        seller_id=order.seller_id,
        product_ids=order.product_ids,
        total_amount=order.total_amount,
        status="pending"
    )
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    return db_order

async def get_order(db: AsyncSession, order_id: int):
    result = await db.get(Order, order_id)
    return result

async def update_order(db: AsyncSession, order_id: int, order_data: OrderUpdate):
    db_order = await db.get(Order, order_id)
    if not db_order:
        return None
    for field, value in order_data.dict(exclude_unset=True).items():
        setattr(db_order, field, value)
    await db.commit()
    await db.refresh(db_order)
    return db_order

async def delete_order(db: AsyncSession, order_id: int):
    db_order = await db.get(Order, order_id)
    if not db_order:
        return False
    await db.delete(db_order)
    await db.commit()
    return True

async def list_orders(
    db: AsyncSession, buyer_id: Optional[int] = None, seller_id: Optional[int] = None
):
    query = select(Order)
    if buyer_id:
        query = query.where(Order.buyer_id == buyer_id)
    if seller_id:
        query = query.where(Order.seller_id == seller_id)
    result = await db.execute(query)
    return result.scalars().all()