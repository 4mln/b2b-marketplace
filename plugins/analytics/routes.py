from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session
from plugins.analytics.schemas import UserActivityResponse, UserActivity

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