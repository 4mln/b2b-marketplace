# plugins/gamification/routes.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/badges")
async def get_badges():
    return {"message": "Badges endpoint works"}