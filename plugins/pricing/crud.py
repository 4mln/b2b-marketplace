# plugins/pricing/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import ProductPrice
from typing import List, Optional

async def get_latest_price(db: AsyncSession, product_id: int) -> Optional[ProductPrice]:
    result = await db.execute(
        select(ProductPrice)
        .where(ProductPrice.product_id == product_id)
        .order_by(ProductPrice.updated_at.desc())
    )
    return result.scalars().first()

async def create_price(db: AsyncSession, price: ProductPrice) -> ProductPrice:
    db.add(price)
    await db.commit()
    await db.refresh(price)
    return price
