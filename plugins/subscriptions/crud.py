from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from plugins.subscriptions.models import SubscriptionPlan, UserSubscription
from plugins.subscriptions.schemas import SubscriptionPlanCreate, UserSubscriptionCreate
from plugins.user.crud import get_user
from datetime import datetime, timedelta

async def create_subscription_plan(db: AsyncSession, plan: SubscriptionPlanCreate):
    db_plan = SubscriptionPlan(**plan.dict())
    db.add(db_plan)
    await db.commit()
    await db.refresh(db_plan)
    return db_plan

async def list_subscription_plans(db: AsyncSession):
    result = await db.execute(select(SubscriptionPlan))
    return result.scalars().all()

async def assign_user_subscription(db: AsyncSession, data: UserSubscriptionCreate):
    # Ensure user exists
    user = await get_user(db, data.user_id)
    if not user:
        raise ValueError("User not found")

    # Ensure plan exists
    plan_result = await db.get(SubscriptionPlan, data.plan_id)
    if not plan_result:
        raise ValueError("Subscription plan not found")

    end_date = datetime.utcnow() + timedelta(days=plan_result.duration_days)
    db_sub = UserSubscription(
        user_id=data.user_id,
        plan_id=data.plan_id,
        end_date=end_date
    )
    db.add(db_sub)
    await db.commit()
    await db.refresh(db_sub)
    return db_sub

async def list_user_subscriptions(db: AsyncSession, user_id: int):
    result = await db.execute(select(UserSubscription).where(UserSubscription.user_id == user_id))
    return result.scalars().all()
