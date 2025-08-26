from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.db import get_session
from plugins.subscriptions.crud import create_subscription_plan, list_subscription_plans, assign_user_subscription, list_user_subscriptions
from plugins.subscriptions.schemas import SubscriptionPlanCreate, SubscriptionPlanOut, UserSubscriptionCreate, UserSubscriptionOut

router = APIRouter()

@router.post("/plans", response_model=SubscriptionPlanOut)
async def create_plan(plan: SubscriptionPlanCreate, db: AsyncSession = Depends(get_session)):
    return await create_subscription_plan(db, plan)

@router.get("/plans", response_model=List[SubscriptionPlanOut])
async def get_plans(db: AsyncSession = Depends(get_session)):
    return await list_subscription_plans(db)

@router.post("/assign", response_model=UserSubscriptionOut)
async def assign_subscription(data: UserSubscriptionCreate, db: AsyncSession = Depends(get_session)):
    try:
        return await assign_user_subscription(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user/{user_id}", response_model=List[UserSubscriptionOut])
async def get_user_subscriptions(user_id: int, db: AsyncSession = Depends(get_session)):
    return await list_user_subscriptions(db, user_id)
