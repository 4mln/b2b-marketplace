from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from plugins.payments.schemas import PaymentCreate, PaymentUpdate, PaymentOut
from plugins.payments.crud import create_payment, get_payment, update_payment, list_payments
from app.core.db import get_session

router = APIRouter()

@router.post("/", response_model=PaymentOut)
async def create_payment_endpoint(payment: PaymentCreate, db: AsyncSession = Depends(get_session)):
    try:
        return await create_payment(db, payment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{payment_id}", response_model=PaymentOut)
async def get_payment_endpoint(payment_id: int, db: AsyncSession = Depends(get_session)):
    db_payment = await get_payment(db, payment_id)
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return db_payment

@router.put("/{payment_id}", response_model=PaymentOut)
async def update_payment_endpoint(payment_id: int, payment_data: PaymentUpdate, db: AsyncSession = Depends(get_session)):
    db_payment = await update_payment(db, payment_id, payment_data)
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return db_payment

@router.get("/", response_model=List[PaymentOut])
async def list_payments_endpoint(order_id: Optional[int] = None, db: AsyncSession = Depends(get_session)):
    return await list_payments(db, order_id)
