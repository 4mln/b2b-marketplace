from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SubscriptionPlanCreate(BaseModel):
    name: str
    price: float
    duration_days: int
    max_users: Optional[int] = None

    model_config = {"extra": "forbid"}

class SubscriptionPlanOut(SubscriptionPlanCreate):
    id: int
    created_at: datetime
    updated_at: datetime

class UserSubscriptionCreate(BaseModel):
    user_id: int
    plan_id: int

class UserSubscriptionOut(UserSubscriptionCreate):
    id: int
    start_date: datetime
    end_date: datetime
    active: bool
    created_at: datetime
    updated_at: datetime
