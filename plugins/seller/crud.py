# plugins/seller/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import Seller
from .schemas import SellerCreate, SellerUpdate

async def create_seller(db: AsyncSession, seller_data: SellerCreate, user_id: int) -> Seller:
    """Create a new seller"""
    new_seller = Seller(**seller_data.dict(), user_id=user_id)
    db.add(new_seller)
    await db.commit()
    await db.refresh(new_seller)
    return new_seller

async def get_seller(db: AsyncSession, seller_id: int) -> Seller | None:
    """Get a seller by ID"""
    return await db.get(Seller, seller_id)

async def update_seller(db: AsyncSession, seller_id: int, seller_data: SellerUpdate, user_id: int) -> Seller | None:
    """Update a seller if user owns it"""
    seller = await db.get(Seller, seller_id)
    if seller and seller.user_id == user_id:
        for key, value in seller_data.dict(exclude_unset=True).items():
            setattr(seller, key, value)
        await db.commit()
        await db.refresh(seller)
        return seller
    return None

async def delete_seller(db: AsyncSession, seller_id: int, user_id: int) -> bool:
    """Delete a seller if user owns it"""
    seller = await db.get(Seller, seller_id)
    if seller and seller.user_id == user_id:
        await db.delete(seller)
        await db.commit()
        return True
    return False

# Optional: additional functions you may have referenced in routes
async def list_sellers(db: AsyncSession, offset: int = 0, limit: int = 10):
    result = await db.execute(select(Seller).offset(offset).limit(limit))
    return result.scalars().all()