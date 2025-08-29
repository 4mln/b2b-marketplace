from pydantic import BaseModel
from datetime import datetime


class BannedItemCreate(BaseModel):
    keyword: str


class BannedItemOut(BannedItemCreate):
    id: int
    created_at: datetime


class AuditLogCreate(BaseModel):
    actor: str
    action: str
    entity: str | None = None


class AuditLogOut(AuditLogCreate):
    id: int
    created_at: datetime


