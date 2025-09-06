from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RatingCreate(BaseModel):
    order_id: int
    ratee_id: int
    quality: float
    timeliness: float
    communication: float
    reliability: float
    comment: Optional[str] = None


class RatingOut(RatingCreate):
    id: int
    rater_id: int
    created_at: datetime












