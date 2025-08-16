# plugins/seller/__init__.py
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from app.core.plugin_loader import PluginBase

class Plugin(PluginBase):
    """Seller plugin"""

    def register_routes(self, app: FastAPI):
        print("🔌 Seller plugin routes registered")
        pass

    async def init_db(self, engine: AsyncEngine):
        if engine:
            print("🗄 Seller plugin DB initialized with engine")