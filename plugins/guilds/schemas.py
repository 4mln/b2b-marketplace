from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class GuildCreate(BaseModel):
    slug: str
    name: str
    description: Optional[str] = None

    model_config = {"extra": "forbid"}


class GuildUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    model_config = {"extra": "forbid"}


class GuildOut(GuildCreate):
    id: int
    created_at: datetime
    updated_at: datetime



