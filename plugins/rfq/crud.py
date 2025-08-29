from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import RFQ, Quote
from .schemas import RFQCreate, QuoteCreate


async def create_rfq(db: AsyncSession, buyer_id: int, data: RFQCreate) -> RFQ:
    rfq = RFQ(buyer_id=buyer_id, **data.dict())
    db.add(rfq)
    await db.commit()
    await db.refresh(rfq)
    return rfq


async def list_rfqs(db: AsyncSession) -> list[RFQ]:
    result = await db.execute(select(RFQ))
    return result.scalars().all()


async def get_rfq(db: AsyncSession, rfq_id: int) -> RFQ | None:
    return await db.get(RFQ, rfq_id)


async def create_quote(db: AsyncSession, seller_id: int, data: QuoteCreate) -> Quote:
    quote = Quote(seller_id=seller_id, **data.dict())
    db.add(quote)
    await db.commit()
    await db.refresh(quote)
    return quote


async def list_quotes_for_rfq(db: AsyncSession, rfq_id: int) -> list[Quote]:
    result = await db.execute(select(Quote).where(Quote.rfq_id == rfq_id))
    return result.scalars().all()


