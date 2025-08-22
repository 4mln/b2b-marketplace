# plugins/user/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .crud import get_user_by_id, create_user
from .schemas import UserOut, UserCreate
from .models import User
from app.core.db import get_session
from plugins.user.security import get_current_user, get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])


# ---------- Get current user ----------
@router.get("/me", response_model=UserOut)
async def read_current_user(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    data = await get_user_by_id(db, current_user.id, include_gamification=True)
    if not data:
        raise HTTPException(status_code=404, detail="User not found")

    return UserOut.model_validate({
        "id": data["user"].id,
        "username": data["user"].username,
        "email": data["user"].email,
        "is_active": data["user"].is_active,
        "is_superuser": data["user"].is_superuser,
        "sellers": data["user"].sellers,
        "buyer": data["user"].buyer,
        "gamification": data["gamification"]
    })


# ---------- Get user by ID ----------
@router.get("/{user_id}", response_model=UserOut)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_session)
):
    data = await get_user_by_id(db, user_id, include_gamification=True)
    if not data:
        raise HTTPException(status_code=404, detail="User not found")

    return UserOut.model_validate({
        "id": data["user"].id,
        "username": data["user"].username,
        "email": data["user"].email,
        "is_active": data["user"].is_active,
        "is_superuser": data["user"].is_superuser,
        "sellers": data["user"].sellers,
        "buyer": data["user"].buyer,
        "gamification": data["gamification"]
    })


# ---------- Create user ----------
@router.post("/", response_model=UserOut)
async def create_user_endpoint(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_session)
):
    hashed_password = get_password_hash(user_in.password)
    user = await create_user(db, user_in.username, user_in.email, hashed_password)

    return UserOut.model_validate({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "sellers": [],
        "buyer": None,
        "gamification": None  # New user has no gamification yet
    })
