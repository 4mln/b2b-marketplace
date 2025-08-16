# plugins/user/__init__.py
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from plugins.user.routes import router as user_router
from app.core.plugin_loader import PluginBase

class Plugin(PluginBase):
    """User plugin: registers routes and optionally initializes DB."""

    _prefix: str = None  # Store prefix on instance

    def register_routes(self, app: FastAPI):
        prefix = "/users"
        app.include_router(user_router, prefix=prefix, tags=["Users"])
        self._prefix = prefix  # ✅ Attach prefix to plugin instance
        print("🔌 User plugin routes registered")

    async def init_db(self, engine: AsyncEngine):
        if engine:
            print("🗄 User plugin DB initialized with engine")
