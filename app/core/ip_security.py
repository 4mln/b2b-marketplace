from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from redis.asyncio import Redis
from datetime import datetime, timedelta
import ipaddress

class IPSecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis: Redis, block_threshold: int = 10, block_duration: int = 3600):
        super().__init__(app)
        self.redis = redis
        self.block_threshold = block_threshold  # Number of suspicious activities before blocking
        self.block_duration = block_duration    # Block duration in seconds
        
    async def is_ip_blocked(self, ip: str) -> bool:
        return await self.redis.exists(f"blocked_ip:{ip}")
    
    async def increment_suspicious_activity(self, ip: str) -> int:
        key = f"suspicious_ip:{ip}"
        count = await self.redis.incr(key)
        if count == 1:
            await self.redis.expire(key, 3600)  # Reset count after 1 hour
        return count
    
    async def block_ip(self, ip: str):
        await self.redis.setex(
            f"blocked_ip:{ip}",
            self.block_duration,
            datetime.utcnow().isoformat()
        )
    
    def is_suspicious_request(self, request: Request) -> bool:
        # Add your suspicious activity detection logic here
        suspicious_patterns = [
            "../",           # Path traversal attempts
            "SELECT ",       # SQL injection attempts
            "<script>",      # XSS attempts
            "/admin",       # Unauthorized admin access
            "wp-admin",     # WordPress scanning
            "phpMyAdmin"    # phpMyAdmin scanning
        ]
        
        path = request.url.path.lower()
        query = str(request.query_params).lower()
        
        return any(pattern.lower() in path or pattern.lower() in query 
                   for pattern in suspicious_patterns)
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        
        # Skip for private IPs (for development)
        if ipaddress.ip_address(client_ip).is_private:
            return await call_next(request)
        
        # Check if IP is blocked
        if await self.is_ip_blocked(client_ip):
            raise HTTPException(
                status_code=403,
                detail="Access denied. Your IP has been blocked due to suspicious activity."
            )
        
        # Check for suspicious activity
        if self.is_suspicious_request(request):
            count = await self.increment_suspicious_activity(client_ip)
            if count >= self.block_threshold:
                await self.block_ip(client_ip)
                raise HTTPException(
                    status_code=403,
                    detail="Access denied. Your IP has been blocked due to suspicious activity."
                )
        
        return await call_next(request)

def setup_ip_security(app: FastAPI, redis: Redis):
    app.add_middleware(
        IPSecurityMiddleware,
        redis=redis,
        block_threshold=10,
        block_duration=3600
    )