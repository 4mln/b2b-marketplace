# plugins/reports/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.db import get_session
from .crud import create_report, get_report, list_reports
from .schemas import ReportCreate, ReportOut, ReportListOut

router = APIRouter(prefix="/reports", tags=["Reports"])

# Create report
@router.post("/", response_model=ReportOut)
async def create_new_report(report_in: ReportCreate, db: AsyncSession = Depends(get_session)):
    return await create_report(db, report_in)

# Get single report
@router.get("/{report_id}", response_model=ReportOut)
async def get_single_report(report_id: int, db: AsyncSession = Depends(get_session)):
    report = await get_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

# List all reports
@router.get("/", response_model=ReportListOut)
async def get_all_reports(db: AsyncSession = Depends(get_session)):
    reports = await list_reports(db)
    return {"items": reports, "total": len(reports)}
