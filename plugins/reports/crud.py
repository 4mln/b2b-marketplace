# plugins/reports/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import Report, ReportData
from .schemas import ReportCreate
from typing import List

# Create a report
async def create_report(db: AsyncSession, report_in: ReportCreate) -> Report:
    report = Report(name=report_in.name, type=report_in.type)
    db.add(report)
    await db.flush()

    # Add report data
    for key, value in (report_in.data or {}).items():
        db.add(ReportData(report_id=report.id, key=key, value=value))

    await db.commit()
    await db.refresh(report)
    return report

# Get report by ID
async def get_report(db: AsyncSession, report_id: int) -> Report | None:
    result = await db.execute(select(Report).where(Report.id == report_id))
    return result.scalars().first()

# List all reports
async def list_reports(db: AsyncSession) -> List[Report]:
    result = await db.execute(select(Report))
    return result.scalars().all()
