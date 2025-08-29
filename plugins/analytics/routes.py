from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session
from plugins.analytics.schemas import UserActivityResponse, UserActivity
from sqlalchemy import select, func
from plugins.products.models import Product
from plugins.rfq.models import RFQ
from plugins.subscriptions.crud import check_plan_limits
from plugins.search.models import SearchEvent

router = APIRouter()

# -----------------------------
# Health check endpoint
# -----------------------------
@router.get("/health", summary="Health check for analytics plugin")
async def health():
    return {"ok": True, "plugin": "analytics"}

# -----------------------------
# Example: fetch user activity
# -----------------------------
@router.get("/user-activity", response_model=UserActivityResponse, summary="Fetch user activity logs")
async def get_user_activity(
    db: AsyncSession = Depends(get_session),
    limit: int = 50
):
    """
    Fetch recent user activity.

    - **limit**: maximum number of records returned (default 50)
    """
    # Placeholder: replace with real DB query
    activities = [
        UserActivity(user_id=1, action="login", timestamp="2025-08-26T12:00:00Z"),
        UserActivity(user_id=2, action="viewed_product", timestamp="2025-08-26T12:01:00Z")
    ][:limit]

    return UserActivityResponse(activities=activities)


# -----------------------------
# Seller dashboard (placeholder aggregates)
# -----------------------------
@router.get("/dashboards/seller/{user_id}")
async def seller_dashboard(user_id: int, db: AsyncSession = Depends(get_session)):
    totals_products = (await db.execute(select(func.count()).select_from(Product).where(Product.seller_id == user_id))).scalar_one()
    plan = await check_plan_limits(user_id, db)
    remaining_products = None
    if plan and plan.max_products is not None:
        remaining_products = max(plan.max_products - totals_products, 0)
    return {
        "totals": {"products": totals_products, "orders": 17, "revenue": 123456.78},
        "remaining": {"products": remaining_products},
        "response_time_hours": 4.2,
        "ads_clicks": 312,
    }


# -----------------------------
# Buyer dashboard (placeholder aggregates)
# -----------------------------
@router.get("/dashboards/buyer/{user_id}")
async def buyer_dashboard(user_id: int, db: AsyncSession = Depends(get_session)):
    totals_rfqs = (await db.execute(select(func.count()).select_from(RFQ).where(RFQ.buyer_id == user_id))).scalar_one()
    plan = await check_plan_limits(user_id, db)
    remaining_rfqs = None
    if plan and plan.max_rfqs is not None:
        remaining_rfqs = max(plan.max_rfqs - totals_rfqs, 0)
    return {
        "totals": {"rfqs": totals_rfqs, "quotes_received": 31, "orders": 5},
        "remaining": {"rfqs": remaining_rfqs},
        "saved_searches": 6,
        "trending_keywords": ["steel", "polymer", "copper"],
    }


@router.get("/search/trending")
async def trending_search_keywords(db: AsyncSession = Depends(get_session), limit: int = 10):
    # naive trending: latest N queries
    result = await db.execute(select(SearchEvent.query).order_by(SearchEvent.created_at.desc()).limit(limit))
    rows = result.all()
    return {"keywords": [r[0] for r in rows]}