from fastapi import APIRouter

router = APIRouter()

@router.get("/info")
async def info():
    return {"info": "extra routes file"}