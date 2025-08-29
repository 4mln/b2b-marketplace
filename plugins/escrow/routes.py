from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session
from sqlalchemy import select, update
from .models import Escrow
from plugins.wallet.integrations import process_marketplace_payment, process_marketplace_refund
from plugins.orders.models import Order


router = APIRouter()


@router.post("/hold")
async def hold_escrow(order_id: int, amount: float, currency: str = "IRR", db: AsyncSession = Depends(get_session)):
    # debit buyer wallet into platform escrow (integration)
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    ok = await process_marketplace_payment(db, user_id=order.buyer_id, amount=amount, currency=currency, reference=f"escrow:{order_id}", description="Escrow hold")
    if not ok:
        raise HTTPException(status_code=400, detail="Payment failed")
    e = Escrow(order_id=order_id, amount=amount, currency=currency)
    db.add(e)
    await db.commit()
    await db.refresh(e)
    return e


@router.post("/{escrow_id}/release")
async def release_escrow(escrow_id: int, db: AsyncSession = Depends(get_session)):
    await db.execute(update(Escrow).where(Escrow.id == escrow_id).set({Escrow.status: "released"}))
    await db.commit()
    e = await db.get(Escrow, escrow_id)
    if not e:
        raise HTTPException(status_code=404, detail="Not found")
    return e


@router.post("/{escrow_id}/refund")
async def refund_escrow(escrow_id: int, db: AsyncSession = Depends(get_session)):
    e = await db.get(Escrow, escrow_id)
    if not e:
        raise HTTPException(status_code=404, detail="Not found")
    order = await db.get(Order, e.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    ok = await process_marketplace_refund(db, user_id=order.buyer_id, amount=e.amount, currency=e.currency, reference=f"escrow:{e.order_id}", description="Escrow refund")
    if not ok:
        raise HTTPException(status_code=400, detail="Refund failed")
    await db.execute(update(Escrow).where(Escrow.id == escrow_id).set({Escrow.status: "refunded"}))
    await db.commit()
    return await db.get(Escrow, escrow_id)


