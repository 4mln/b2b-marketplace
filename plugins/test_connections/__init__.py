from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from .routes import router
from app.core.plugin_loader import PluginBase


class Plugin(PluginBase):
    def register_routes(self, app: FastAPI):
        app.include_router(router, prefix="/connections", tags=["Connections"])

    async def init_db(self, engine: AsyncEngine):
        # You can initialize DB tables or connections here if needed
        pass