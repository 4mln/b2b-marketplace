from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session
from .crud import get_user_by_id

# Placeholder: in production, replace with JWT authentication
async def get_current_user(db: AsyncSession = Depends(get_session)):
    # For now, return a fake user
    user = await get_user_by_id(db, user_id=1)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
