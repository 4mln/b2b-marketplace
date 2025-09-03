from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.db import get_session
from plugins.subscriptions.crud import create_subscription_plan, list_subscription_plans, assign_user_subscription, list_user_subscriptions
from plugins.subscriptions.schemas import SubscriptionPlanCreate, SubscriptionPlanOut, UserSubscriptionCreate, UserSubscriptionOut
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import update
from plugins.subscriptions.models import SubscriptionPlan

router = APIRouter()

@router.post("/plans", response_model=SubscriptionPlanOut)
async def create_plan(plan: SubscriptionPlanCreate, db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    return await create_subscription_plan(db, plan)

@router.get("/plans", response_model=List[SubscriptionPlanOut])
async def get_plans(db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    return await list_subscription_plans(db)

@router.post("/assign", response_model=UserSubscriptionOut)
async def assign_subscription(data: UserSubscriptionCreate, db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    try:
        return await assign_user_subscription(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user/{user_id}", response_model=List[UserSubscriptionOut])
async def get_user_subscriptions(user_id: int, db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    return await list_user_subscriptions(db, user_id)


class SubscriptionPlanPatch(BaseModel):
    price: Optional[float] = None
    duration_days: Optional[int] = None
    max_users: Optional[int] = None
    max_products: Optional[int] = None
    max_rfqs: Optional[int] = None
    boost_multiplier: Optional[float] = None


@router.patch("/plans/{plan_id}", response_model=SubscriptionPlanOut)
async def patch_plan(plan_id: int, payload: SubscriptionPlanPatch, db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    values = {k: v for k, v in payload.dict(exclude_unset=True).items()}
    if not values:
        plan = await db.get(SubscriptionPlan, plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        return plan
    await db.execute(update(SubscriptionPlan).where(SubscriptionPlan.id == plan_id).values(**values))
    await db.commit()
    plan = await db.get(SubscriptionPlan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan
