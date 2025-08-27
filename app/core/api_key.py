from fastapi import FastAPI, Request, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from redis.asyncio import Redis
from datetime import datetime, timedelta
import secrets
import json

API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

class APIKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, redis: Redis):
        self.redis = redis
    
    async def get_api_key_info(self, api_key: str) -> dict:
        key_info = await self.redis.get(f"api_key:{api_key}")
        return json.loads(key_info) if key_info else None
    
    async def dispatch(self, request: Request, call_next):
        # Skip API key check for non-API routes and authentication endpoints
        if not request.url.path.startswith("/api/") or request.url.path.startswith("/api/auth"):
            return await call_next(request)
        
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            raise HTTPException(
                status_code=401,
                detail="API key is missing"
            )
        
        key_info = await self.get_api_key_info(api_key)
        if not key_info:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )
        
        # Check if key is expired
        if key_info.get("expires_at") and datetime.fromisoformat(key_info["expires_at"]) < datetime.utcnow():
            raise HTTPException(
                status_code=401,
                detail="API key has expired"
            )
        
        # Add API key info to request state
        request.state.api_key_info = key_info
        
        return await call_next(request)

class APIKeyManager:
    def __init__(self, redis: Redis):
        self.redis = redis
    
    async def create_api_key(self, client_id: str, expires_in_days: int = 365) -> dict:
        api_key = secrets.token_urlsafe(32)
        expires_at = (datetime.utcnow() + timedelta(days=expires_in_days)).isoformat()
        
        key_info = {
            "client_id": client_id,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at,
            "scopes": ["read", "write"]  # Default scopes
        }
        
        # Store API key info
        await self.redis.set(
            f"api_key:{api_key}",
            json.dumps(key_info),
            ex=expires_in_days * 86400
        )
        
        return {"api_key": api_key, **key_info}
    
    async def revoke_api_key(self, api_key: str):
        await self.redis.delete(f"api_key:{api_key}")
    
    async def update_api_key_scopes(self, api_key: str, scopes: list):
        key_info = await self.redis.get(f"api_key:{api_key}")
        if not key_info:
            raise ValueError("API key not found")
        
        info = json.loads(key_info)
        info["scopes"] = scopes
        
        # Calculate remaining TTL
        expires_at = datetime.fromisoformat(info["expires_at"])
        ttl = int((expires_at - datetime.utcnow()).total_seconds())
        
        if ttl > 0:
            await self.redis.set(
                f"api_key:{api_key}",
                json.dumps(info),
                ex=ttl
            )

def setup_api_key_management(app: FastAPI, redis: Redis) -> APIKeyManager:
    app.add_middleware(APIKeyMiddleware, redis=redis)
    return APIKeyManager(redis)