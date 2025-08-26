# plugins/test_connections/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import ConnectionTest
from typing import List

async def create_test(db: AsyncSession, test: ConnectionTest) -> ConnectionTest:
    db.add(test)
    await db.commit()
    await db.refresh(test)
    return test

async def get_tests(db: AsyncSession, limit: int = 50) -> List[ConnectionTest]:
    result = await db.execute(select(ConnectionTest).limit(limit))
    return result.scalars().all()
