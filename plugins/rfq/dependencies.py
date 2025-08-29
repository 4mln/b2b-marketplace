from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.db import get_session
from plugins.subscriptions.crud import check_plan_limits
from plugins.rfq.models import RFQ


async def enforce_rfq_limit(user_id: int, db: AsyncSession = Depends(get_session)):
    plan = await check_plan_limits(user_id, db)
    if not plan:
        raise HTTPException(status_code=403, detail="No active subscription")

    result = await db.execute(
        select(func.count()).select_from(RFQ).where(RFQ.buyer_id == user_id)
    )
    count = result.scalar_one()
    if plan.max_rfqs is not None and count >= plan.max_rfqs:
        raise HTTPException(status_code=403, detail="RFQ limit reached for your subscription")


