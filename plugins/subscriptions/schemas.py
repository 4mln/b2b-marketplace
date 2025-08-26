from pydantic import BaseModel
from datetime import datetime

class SubscriptionPlanCreate(BaseModel):
    name: str
    max_products: int
    max_orders: int
    price: int
    duration_days: int

    model_config = {"extra": "forbid"}

class SubscriptionPlanOut(SubscriptionPlanCreate):
    id: int
    active: bool

    model_config = {"extra": "forbid"}

class UserSubscriptionCreate(BaseModel):
    user_id: int
    plan_id: int

    model_config = {"extra": "forbid"}

class UserSubscriptionOut(UserSubscriptionCreate):
    id: int
    start_date: datetime
    end_date: datetime
    active: bool

    model_config = {"extra": "forbid"}