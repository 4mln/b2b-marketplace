from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Security Headers
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' data: https:; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        
        return response

def setup_security_middleware(app: FastAPI):
    app.add_middleware(SecurityHeadersMiddleware)


def verify_user_role(user, required_role: str) -> bool:
    """Minimal role checker used by some plugins.
    Returns True if user's role matches or user is superuser.
    """
    role = getattr(user, "role", None)
    is_superuser = getattr(user, "is_superuser", False)
    return bool(is_superuser or (role == required_role))