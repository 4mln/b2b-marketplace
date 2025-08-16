from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session
from .crud import get_user_by_id
from .security import get_current_user

router = APIRouter()

@router.get("/me")
async def read_current_user(current_user = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "email": current_user.email}