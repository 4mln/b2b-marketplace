from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.db import get_session
from plugins.subscriptions.models import SubscriptionPlan, UserSubscription
from plugins.subscriptions.schemas import (
    SubscriptionPlanCreate,
    SubscriptionPlanOut,
    UserSubscriptionCreate,
    UserSubscriptionOut
)

router = APIRouter()

# CRUD for Subscription Plans
@router.post("/plans", response_model=SubscriptionPlanOut)
async def create_plan(plan: SubscriptionPlanCreate, db: AsyncSession = Depends(get_session)):
    new_plan = SubscriptionPlan(**plan.model_dump())
    db.add(new_plan)
    await db.commit()
    await db.refresh(new_plan)
    return new_plan

@router.get("/plans", response_model=List[SubscriptionPlanOut])
async def list_plans(db: AsyncSession = Depends(get_session)):
    result = await db.execute("SELECT * FROM subscription_plans")
    plans = result.scalars().all()
    return plans

# CRUD for User Subscriptions
@router.post("/user", response_model=UserSubscriptionOut)
async def assign_subscription(sub: UserSubscriptionCreate, db: AsyncSession = Depends(get_session)):
    new_sub = UserSubscription(**sub.model_dump())
    db.add(new_sub)
    await db.commit()
    await db.refresh(new_sub)
    return new_sub

@router.get("/user", response_model=List[UserSubscriptionOut])
async def list_user_subscriptions(db: AsyncSession = Depends(get_session)):
    result = await db.execute("SELECT * FROM user_subscriptions")
    subs = result.scalars().all()
    return subs