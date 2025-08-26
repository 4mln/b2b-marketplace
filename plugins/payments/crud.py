from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from plugins.payments.models import Payment, PaymentStatus
from plugins.payments.schemas import PaymentCreate, PaymentUpdate
from plugins.orders.crud import get_order
from sqlalchemy.exc import SQLAlchemyError

async def create_payment(db: AsyncSession, payment: PaymentCreate):
    # Validate order existence
    db_order = await get_order(db, payment.order_id)
    if not db_order:
        raise ValueError("Order not found")

    # Prevent duplicate payment for the same order if already completed
    existing = await db.execute(
        select(Payment).where(Payment.order_id == payment.order_id, Payment.status == PaymentStatus.completed)
    )
    if existing.scalar_one_or_none():
        raise ValueError("Payment already completed for this order")

    db_payment = Payment(
        order_id=payment.order_id,
        amount=payment.amount,
        provider=payment.provider,
        status=PaymentStatus.pending
    )
    try:
        db.add(db_payment)
        await db.commit()
        await db.refresh(db_payment)
    except SQLAlchemyError:
        await db.rollback()
        raise
    return db_payment

async def get_payment(db: AsyncSession, payment_id: int):
    result = await db.get(Payment, payment_id)
    return result

async def update_payment(db: AsyncSession, payment_id: int, payment_data: PaymentUpdate):
    db_payment = await get_payment(db, payment_id)
    if not db_payment:
        return None
    for field, value in payment_data.dict(exclude_unset=True).items():
        setattr(db_payment, field, value)
    await db.commit()
    await db.refresh(db_payment)
    return db_payment

async def list_payments(db: AsyncSession, order_id: Optional[int] = None):
    query = select(Payment)
    if order_id:
        query = query.where(Payment.order_id == order_id)
    result = await db.execute(query)
    return result.scalars().all()
