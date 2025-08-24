from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import asc, desc
from typing import List, Optional
from .models import Buyer
from .schemas import BuyerCreate, BuyerUpdate

# -----------------------------
# Create
# -----------------------------
async def create_buyer(db: AsyncSession, buyer_data: BuyerCreate, user_id: int) -> Buyer:
    buyer_dict = buyer_data.dict()
    buyer_dict["user_id"] = user_id
    buyer = Buyer(**buyer_dict)
    db.add(buyer)
    await db.commit()
    await db.refresh(buyer)
    return buyer

# -----------------------------
# Read by ID
# -----------------------------
async def get_buyer(db: AsyncSession, buyer_id: int) -> Optional[Buyer]:
    result = await db.execute(select(Buyer).where(Buyer.id == buyer_id))
    return result.scalars().first()

# -----------------------------
# Update
# -----------------------------
async def update_buyer(db: AsyncSession, buyer_id: int, buyer_data: BuyerUpdate, user_id: int) -> Optional[Buyer]:
    buyer = await get_buyer(db, buyer_id)
    if not buyer or buyer.user_id != user_id:
        return None
    for key, value in buyer_data.dict(exclude_unset=True).items():
        setattr(buyer, key, value)
    db.add(buyer)
    await db.commit()
    await db.refresh(buyer)
    return buyer

# -----------------------------
# Delete
# -----------------------------
async def delete_buyer(db: AsyncSession, buyer_id: int, user_id: int) -> bool:
    buyer = await get_buyer(db, buyer_id)
    if not buyer or buyer.user_id != user_id:
        return False
    await db.delete(buyer)
    await db.commit()
    return True

# -----------------------------
# List buyers with pagination & optional search
# -----------------------------
async def list_buyers(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "id",
    sort_dir: str = "asc",
    search: Optional[str] = None
) -> List[Buyer]:
    sort_column = getattr(Buyer, sort_by, None)
    if not sort_column:
        raise ValueError(f"Invalid sort field: {sort_by}")
    order = asc(sort_column) if sort_dir == "asc" else desc(sort_column)

    query = select(Buyer)
    if search:
        query = query.where(Buyer.name.ilike(f"%{search}%") | Buyer.email.ilike(f"%{search}%"))
    query = query.order_by(order).offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    return result.scalars().all()