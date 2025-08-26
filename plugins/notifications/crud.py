# plugins/notifications/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import Notification
from typing import List

async def create_notification(db: AsyncSession, notification: Notification) -> Notification:
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification

async def get_user_notifications(db: AsyncSession, user_id: int, limit: int = 50) -> List[Notification]:
    result = await db.execute(
        select(Notification).where(Notification.user_id == user_id).limit(limit)
    )
    return result.scalars().all()
