# app/api/routes.py
from fastapi import APIRouter, Depends
from app.core.config import settings
from plugins.user.routes import router as user_router
from plugins.auth.routes import router as auth_router

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Import and include plugin routers
def setup_api_routes(app):
    # Register the main API router
    app.include_router(api_router)
    app.include_router(user_router)
    app.include_router(auth_router)
    # The plugins will register their own routes with the app directly
    # This function is called from main.py after plugins are loaded