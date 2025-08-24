# plugins/gamification/routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.db import get_session
from plugins.gamification.models import Badge, UserPoints
from plugins.gamification.schemas import BadgeOut, AwardPoints, AssignBadge
from plugins.user.models import User

router = APIRouter(prefix="/gamification", tags=["Gamification"])

# -----------------------------
# Award points to a user
# -----------------------------
@router.post("/points", response_model=dict)
async def award_points_to_user(
    data: AwardPoints,
    db: AsyncSession = Depends(get_session)
):
    user = await db.get(User, data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_points = await db.get(UserPoints, data.user_id)
    if not user_points:
        user_points = UserPoints(user_id=data.user_id, points=0)
        db.add(user_points)

    user_points.points += data.points
    await db.commit()
    await db.refresh(user_points)

    return {"user_id": user_points.user_id, "points": user_points.points}

# -----------------------------
# Assign badge to user
# -----------------------------
@router.post("/badges", response_model=BadgeOut)
async def assign_badge_to_user(
    data: AssignBadge,
    db: AsyncSession = Depends(get_session)
):
    user = await db.get(User, data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    badge = Badge(user_id=data.user_id, badge_type=data.badge_type)
    db.add(badge)
    await db.commit()
    await db.refresh(badge)

    return badge

# -----------------------------
# Get all badges for a user
# -----------------------------
@router.get("/badges/{user_id}", response_model=List[BadgeOut])
async def get_user_badges(
    user_id: int,
    db: AsyncSession = Depends(get_session)
):
    result = await db.execute(
        select(Badge).where(Badge.user_id == user_id)
    )
    return result.scalars().all()

# -----------------------------
# Get user points
# -----------------------------
@router.get("/points/{user_id}", response_model=dict)
async def get_user_points(
    user_id: int,
    db: AsyncSession = Depends(get_session)
):
    user_points = await db.get(UserPoints, user_id)
    if not user_points:
        return {"user_id": user_id, "points": 0}
    return {"user_id": user_id, "points": user_points.points}