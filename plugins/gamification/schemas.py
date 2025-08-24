from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

# -----------------------------
# Badge Types
# -----------------------------
class BadgeTypeEnum(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    CUSTOM = "custom"

# -----------------------------
# Badge Output
# -----------------------------
class BadgeOut(BaseModel):
    name: str
    description: str
    type: BadgeTypeEnum = BadgeTypeEnum.CUSTOM
    icon_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# -----------------------------
# Leaderboard Entry
# -----------------------------
class LeaderboardEntry(BaseModel):
    username: str
    score: int
    rank: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

# -----------------------------
# User Gamification Progress
# -----------------------------
class GamificationProgress(BaseModel):
    user_id: int
    points: int = 0
    level: int = 1
    badges: List[str] = []
    achievements: Dict[str, bool] = {}
    last_updated: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# -----------------------------
# Create / Update Schemas
# -----------------------------
class GamificationUpdate(BaseModel):
    points: Optional[int] = None
    level: Optional[int] = None
    badges: Optional[List[str]] = None
    achievements: Optional[Dict[str, bool]] = None

    model_config = ConfigDict(from_attributes=True)

class GamificationCreate(BaseModel):
    user_id: int
    points: int = 0
    level: int = 1
    badges: List[str] = []
    achievements: Dict[str, bool] = {}

    model_config = ConfigDict(from_attributes=True)

# -----------------------------
# Request Schemas for Routes
# -----------------------------
class AwardPoints(BaseModel):
    user_id: int
    points: int

class AssignBadge(BaseModel):
    user_id: int
    name: str
    description: str
    badge_type: BadgeTypeEnum = BadgeTypeEnum.CUSTOM

# -----------------------------
# Response / List Models
# -----------------------------
class GamificationList(BaseModel):
    items: List[GamificationProgress]
    total: int

    model_config = ConfigDict(from_attributes=True)

class LeaderboardOut(BaseModel):
    leaderboard: List[LeaderboardEntry]

    model_config = ConfigDict(from_attributes=True)

# -----------------------------
# Explicit Exports
# -----------------------------
__all__ = [
    "BadgeTypeEnum",
    "BadgeOut",
    "LeaderboardEntry",
    "GamificationProgress",
    "GamificationUpdate",
    "GamificationCreate",
    "GamificationList",
    "LeaderboardOut",
    "AwardPoints",
    "AssignBadge",
]