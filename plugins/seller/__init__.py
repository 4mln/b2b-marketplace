# plugins/seller/__init__.py
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from app.core.plugin_loader import PluginBase
from .routes import router as seller_router  # import the actual router

class Plugin(PluginBase):
    """Seller plugin"""

    def register_routes(self, app: FastAPI):
        app.include_router(seller_router)  # this registers the /sellers routes
        print("🔌 Seller plugin routes registered")

    async def init_db(self, engine: AsyncEngine):
        if engine:
            print("🗄 Seller plugin DB initialized with engine")