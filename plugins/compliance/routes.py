from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import BannedItemCreate, BannedItemOut, ComplianceAuditLogCreate, ComplianceAuditLogOut
from . import crud


router = APIRouter()


@router.post("/banned-items", response_model=BannedItemOut)
async def add_banned_item(payload: BannedItemCreate, db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    return await crud.add_banned_item(db, payload)


@router.get("/banned-items", response_model=list[BannedItemOut])
async def list_banned_items(db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    return await crud.list_banned_items(db)


@router.post("/audit", response_model=ComplianceAuditLogOut)
async def create_audit_log(payload: ComplianceAuditLogCreate, db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    return await crud.write_audit_log(db, payload)


@router.get("/audit", response_model=list[ComplianceAuditLogOut])
async def list_audit_log(db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    return await crud.list_audit_logs(db)








