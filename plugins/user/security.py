from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session
from .crud import get_user_by_id
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Placeholder: in production, replace with JWT authentication
async def get_current_user(db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    # For now, return a fake user
    user = await get_user_by_id(db, user_id=1)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
