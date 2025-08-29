from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session
from plugins.user.security import get_current_user
from plugins.user.models import User
from .schemas import RatingCreate, RatingOut
from . import crud


router = APIRouter()


@router.post("/", response_model=RatingOut)
async def create_rating_endpoint(
    payload: RatingCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    return await crud.create_rating(db, rater_id=user.id, data=payload)


@router.get("/user/{user_id}", response_model=list[RatingOut])
async def list_ratings_for_user_endpoint(user_id: int, db: AsyncSession = Depends(get_session)):
    return await crud.list_ratings_for_user(db, user_id)


