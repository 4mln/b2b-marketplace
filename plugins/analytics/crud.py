# plugins/analytics/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import AnalyticsEvent
from typing import List

async def create_event(db: AsyncSession, event: AnalyticsEvent) -> AnalyticsEvent:
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event

async def get_events(db: AsyncSession, limit: int = 100) -> List[AnalyticsEvent]:
    result = await db.execute(select(AnalyticsEvent).limit(limit))
    return result.scalars().all()
