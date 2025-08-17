# plugins/auth/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.core.db import get_session  # your async session dependency
from plugins.auth.schemas import UserCreate, UserOut, Token
from plugins.auth.auth_utils import hash_password, authenticate_user, get_user_by_email
from plugins.auth.jwt import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

# -----------------------------
# Signup endpoint
# -----------------------------
@router.post("/signup", response_model=UserOut)
async def signup(user_in: UserCreate, db: AsyncSession = Depends(get_session)):
    existing_user = await get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    from plugins.auth.models import User  # import here to avoid circular imports
    new_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hash_password(user_in.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

# -----------------------------
# Login endpoint
# -----------------------------
@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session)
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}