# plugins/auth/__init__.py
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from plugins.auth.routes import router as auth_router  # if you have routes
from app.core.plugin_loader import PluginBase

class Plugin(PluginBase):
    """Auth plugin: registers routes and optionally initializes DB."""

    def register_routes(self, app: FastAPI):
        # Include your auth routes if any
        app.include_router(auth_router, prefix="/auth", tags=["Auth"])
        print("🔌 Auth plugin routes registered")

    async def init_db(self, engine: AsyncEngine):
        if engine:
            print("🗄 Auth plugin DB initialized with engine")
