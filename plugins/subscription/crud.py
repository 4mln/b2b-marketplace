from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from plugins.subscriptions.models import SubscriptionPlan, UserSubscription
from datetime import datetime

async def get_active_subscription(user_id: int, db: AsyncSession) -> UserSubscription | None:
    """Return the currently active subscription for a user."""
    result = await db.execute(
        select(UserSubscription).where(
            UserSubscription.user_id == user_id,
            UserSubscription.active == True,
            UserSubscription.start_date <= datetime.utcnow(),
            UserSubscription.end_date >= datetime.utcnow()
        )
    )
    return result.scalar_one_or_none()

async def check_plan_limits(user_id: int, db: AsyncSession) -> SubscriptionPlan | None:
    """Return the active plan and its limits for a user."""
    sub = await get_active_subscription(user_id, db)
    if not sub:
        return None
    return sub.plan