# plugins/gamification/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime

from .models import Badge, UserBadge, BadgeTypeEnum
from .schemas import BadgeOut, GamificationProgress

# ---------- Get all badges ----------
async def get_all_badges(db: AsyncSession) -> List[BadgeOut]:
    result = await db.execute(select(Badge))
    badges = result.scalars().all()
    return [
        BadgeOut.model_validate({
            "id": b.id,
            "name": b.name,
            "description": b.description,
            "points_required": b.points_required,
            "icon_url": b.icon_url,
            "created_at": b.created_at
        })
        for b in badges
    ]


# ---------- Get badges for a specific user ----------
async def get_user_badges(db: AsyncSession, user_id: int) -> List[BadgeOut]:
    result = await db.execute(
        select(UserBadge)
        .where(UserBadge.user_id == user_id)
        .options(selectinload(UserBadge.badge))
    )
    user_badges: List[UserBadge] = result.scalars().all()

    badges_out = []
    for ub in user_badges:
        badge = ub.badge
        badges_out.append(
            BadgeOut.model_validate({
                "id": badge.id,
                "name": badge.name,
                "description": badge.description,
                "points_required": badge.points_required,
                "icon_url": badge.icon_url,
                "created_at": badge.created_at
            })
        )
    return badges_out


# ---------- Get gamification progress for a user ----------
async def get_gamification_progress(db: AsyncSession, user_id: int) -> GamificationProgress:
    badges = await get_user_badges(db, user_id)
    total_points = sum(b.points_required for b in badges)
    level = max(1, total_points // 100 + 1)  # Every 100 points = 1 level

    return GamificationProgress.model_validate({
        "user_id": user_id,
        "total_points": total_points,
        "level": level,
        "badges": badges
    })


# ---------- Award badge to a user ----------
async def award_badge_to_user(db: AsyncSession, user_id: int, badge_id: int) -> BadgeOut:
    # Check if user already has badge
    existing = await db.execute(
        select(UserBadge)
        .where(UserBadge.user_id == user_id, UserBadge.badge_id == badge_id)
    )
    if existing.scalar_one_or_none():
        raise ValueError("User already has this badge")

    user_badge = UserBadge(
        user_id=user_id,
        badge_id=badge_id,
        awarded_at=datetime.utcnow()  # ensure UTC timestamp
    )
    db.add(user_badge)
    await db.commit()
    await db.refresh(user_badge)

    badge = await db.get(Badge, badge_id)
    return BadgeOut.model_validate({
        "id": badge.id,
        "name": badge.name,
        "description": badge.description,
        "points_required": badge.points_required,
        "icon_url": badge.icon_url,
        "created_at": badge.created_at
    })