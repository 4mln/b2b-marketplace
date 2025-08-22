from fastapi import APIRouter
from app.core.plugin_loader import PluginBase
from plugins.auth import routes

class Plugin(PluginBase):
    """Auth plugin"""

    def register_routes(self, app):
        app.include_router(routes.router, prefix="/auth", tags=["auth"])

    async def init_db(self, engine):
        # Optional async DB init
        pass