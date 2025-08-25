from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import asc, desc
from typing import List
from .models import User
from .schemas import UserCreate, UserUpdate

# -----------------------------
# Create
# -----------------------------
async def create_user(db: AsyncSession, user_data: UserCreate):
    user = User(**user_data.dict())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

# -----------------------------
# Read by ID
# -----------------------------
async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()
get_user_by_id = get_user
# -----------------------------
# Update
# -----------------------------
async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate):
    user = await get_user(db, user_id)
    if not user:
        return None
    for key, value in user_data.dict(exclude_unset=True).items():
        setattr(user, key, value)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

# -----------------------------
# Delete
# -----------------------------
async def delete_user(db: AsyncSession, user_id: int):
    user = await get_user(db, user_id)
    if not user:
        return False
    await db.delete(user)
    await db.commit()
    return True

# -----------------------------
# Get all users (pagination & sorting)
# -----------------------------
async def get_all_users(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "id",
    sort_dir: str = "asc"
) -> List[User]:
    sort_column = getattr(User, sort_by, None)
    if not sort_column:
        raise ValueError(f"Invalid sort field: {sort_by}")
    order = asc(sort_column) if sort_dir == "asc" else desc(sort_column)

    result = await db.execute(
        select(User)
        .order_by(order)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return result.scalars().all()

async def list_users(db: AsyncSession):
    return await db.execute(select(User))

# -----------------------------
# Search users by name or email
# -----------------------------
async def search_users(
    db: AsyncSession,
    query: str,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "id",
    sort_dir: str = "asc"
) -> List[User]:
    sort_column = getattr(User, sort_by, None)
    if not sort_column:
        raise ValueError(f"Invalid sort field: {sort_by}")
    order = asc(sort_column) if sort_dir == "asc" else desc(sort_column)

    result = await db.execute(
        select(User)
        .where(User.name.ilike(f"%{query}%") | User.email.ilike(f"%{query}%"))
        .order_by(order)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return result.scalars().all()