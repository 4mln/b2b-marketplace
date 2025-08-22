from __future__ import annotations
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum as PyEnum

class BadgeTypeEnum(str, PyEnum):
    FREE = "FREE"
    BASIC = "BASIC"
    PREMIUM = "PREMIUM"

class BadgeBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: Optional[BadgeTypeEnum] = BadgeTypeEnum.FREE

class BadgeCreate(BadgeBase):
    points_required: Optional[int] = 0
    icon_url: Optional[str] = None

class BadgeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[BadgeTypeEnum] = None
    points_required: Optional[int] = None
    icon_url: Optional[str] = None

class BadgeOut(BadgeBase):
    id: int
    points_required: int
    icon_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

class UserBadgeOut(BaseModel):
    user_id: int
    badge_id: int
    awarded_at: datetime

    model_config = {"from_attributes": True}

class GamificationProgress(BaseModel):
    user_id: int
    total_points: int = 0
    level: int = 1
    badges: List[BadgeOut] = []

    model_config = {"from_attributes": True}

GamificationProgress.model_rebuild()
BadgeOut.model_rebuild()
UserBadgeOut.model_rebuild()