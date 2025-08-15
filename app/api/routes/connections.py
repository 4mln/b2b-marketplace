from fastapi import APIRouter
import redis.asyncio as redis
from app.core.config import settings

router = APIRouter()

@router.get("/connections/test-redis")
async def test_redis():
    r = redis.from_url(settings.REDIS_URL, decode_responses=True)
    await r.set("test_key", "Hello from Redis!")
    value = await r.get("test_key")
    return {"status": "ok", "redis_value": value}