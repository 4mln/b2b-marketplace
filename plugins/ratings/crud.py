from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import Rating
from .schemas import RatingCreate
from sqlalchemy import func, select


async def create_rating(db: AsyncSession, rater_id: int, data: RatingCreate) -> Rating:
    rating = Rating(rater_id=rater_id, **data.dict())
    db.add(rating)
    await db.commit()
    await db.refresh(rating)
    return rating


async def list_ratings_for_user(db: AsyncSession, user_id: int) -> list[Rating]:
    result = await db.execute(select(Rating).where(Rating.ratee_id == user_id))
    return result.scalars().all()


async def get_reputation_score(db: AsyncSession, user_id: int) -> float:
    row = await db.execute(
        select(
            (func.avg(Rating.quality) + func.avg(Rating.timeliness) + func.avg(Rating.communication) + func.avg(Rating.reliability)) / 4.0
        ).where(Rating.ratee_id == user_id)
    )
    score = row.scalar()
    return float(score or 0.0)


