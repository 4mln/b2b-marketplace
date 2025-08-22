# plugins/gamification/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from .crud import get_all_badges, get_user_badges, get_gamification_progress, award_badge_to_user
from .schemas import BadgeOut, GamificationProgress
from app.core.db import get_session
from plugins.user.security import get_current_user
from plugins.user.models import User

router = APIRouter(prefix="/gamification", tags=["Gamification"])

# ---------- Get all badges ----------
@router.get("/badges", response_model=List[BadgeOut])
async def list_badges(db: AsyncSession = Depends(get_session)):
    return await get_all_badges(db)

# ---------- Get badges of current user ----------
@router.get("/me/badges", response_model=List[BadgeOut])
async def list_my_badges(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    return await get_user_badges(db, current_user.id)

# ---------- Get gamification progress of current user ----------
@router.get("/me/progress", response_model=GamificationProgress)
async def my_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    return await get_gamification_progress(db, current_user.id)

# ---------- Award badge to current user ----------
@router.post("/me/badges/{badge_id}", response_model=BadgeOut)
async def award_badge(
    badge_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    try:
        return await award_badge_to_user(db, current_user.id, badge_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))