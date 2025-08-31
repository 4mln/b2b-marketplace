from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from app.core.config import settings
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis: Redis):
        super().__init__(app)
        self.redis = redis
        self.window = settings.RATE_LIMIT_WINDOW_SECONDS
        self.max_requests = settings.RATE_LIMIT_MAX_REQUESTS

    async def check_rate_limit(self, key: str) -> bool:
        current = int(time.time())
        window_start = current - self.window
        
        async with self.redis.pipeline() as pipe:
            # Remove old requests
            await pipe.zremrangebyscore(key, 0, window_start)
            # Add current request
            await pipe.zadd(key, {str(current): current})
            # Count requests in window
            await pipe.zcard(key)
            # Set expiry on the key
            await pipe.expire(key, self.window)
            _, _, requests_count, _ = await pipe.execute()

        return requests_count <= self.max_requests

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for non-API routes
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        # Create rate limit key based on IP and endpoint
        key = f"rate_limit:{request.client.host}:{request.url.path}"

        if not await self.check_rate_limit(key):
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please try again later."
                }
            )

        return await call_next(request)


class LocaleMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        accept_language = request.headers.get("Accept-Language", "")
        locale = "fa" if "fa" in accept_language.lower() else "en"
        direction = "rtl" if locale == "fa" else "ltr"
        response = await call_next(request)
        response.headers["Content-Language"] = locale
        response.headers["X-Text-Direction"] = direction
        return response

def setup_middleware(app: FastAPI, redis: Redis):
    app.add_middleware(RateLimitMiddleware, redis=redis)
    app.add_middleware(LocaleMiddleware)