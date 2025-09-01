from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import BannedItem, ComplianceAuditLog
from .schemas import BannedItemCreate, ComplianceAuditLogCreate


async def add_banned_item(db: AsyncSession, data: BannedItemCreate) -> BannedItem:
    item = BannedItem(**data.dict())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def list_banned_items(db: AsyncSession) -> list[BannedItem]:
    result = await db.execute(select(BannedItem))
    return result.scalars().all()


async def write_audit_log(db: AsyncSession, data: ComplianceAuditLogCreate) -> ComplianceAuditLog:
    log = ComplianceAuditLog(**data.dict())
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


async def list_audit_logs(db: AsyncSession) -> list[ComplianceAuditLog]:
    result = await db.execute(select(ComplianceAuditLog))
    return result.scalars().all()








