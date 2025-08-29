from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class CampaignCreate(BaseModel):
    name: str
    budget: float
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    targeting: Optional[Any] = None


class CampaignOut(CampaignCreate):
    id: int
    owner_id: int
    active: bool
    created_at: datetime


class PlacementCreate(BaseModel):
    campaign_id: int
    type: str


class PlacementOut(PlacementCreate):
    id: int
    budget_spent: float
    metrics: Optional[Any]
    created_at: datetime


