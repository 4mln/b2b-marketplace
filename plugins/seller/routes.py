from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import Seller
from .schemas import SellerCreate, SellerUpdate

router = APIRouter(prefix="/sellers", tags=["Sellers"])

async def create_seller(db: AsyncSession, seller: SellerCreate, user_id: int) -> Seller:
    db_seller = Seller(**seller.dict(), user_id=user_id)
    db.add(db_seller)
    await db.commit()
    await db.refresh(db_seller)
    return db_seller

async def get_seller(db: AsyncSession, seller_id: int) -> Seller | None:
    result = await db.execute(select(Seller).where(Seller.id == seller_id))
    return result.scalars().first()

async def update_seller(db: AsyncSession, seller_id: int, seller_data: SellerUpdate, user_id: int) -> Seller | None:
    db_seller = await get_seller(db, seller_id)
    if not db_seller or db_seller.user_id != user_id:
        return None
    for key, value in seller_data.dict(exclude_unset=True).items():
        setattr(db_seller, key, value)
    await db.commit()
    await db.refresh(db_seller)
    return db_seller

async def delete_seller(db: AsyncSession, seller_id: int, user_id: int) -> bool:
    db_seller = await get_seller(db, seller_id)
    if not db_seller or db_seller.user_id != user_id:
        return False
    await db.delete(db_seller)
    await db.commit()
    return True