# plugins/test_connections/__init__.py
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from app.core.plugin_loader import PluginBase

class Plugin(PluginBase):
    """Test Connections plugin"""

    def register_routes(self, app: FastAPI):
        print("🔌 Test Connections plugin routes registered")
        pass

    async def init_db(self, engine: AsyncEngine):
        if engine:
            print("🗄 Test Connections plugin DB initialized with engine")
