from app.core.plugin_loader import PluginBase
from plugins.user import routes

class Plugin(PluginBase):
    """User plugin"""

    def register_routes(self, app):
        app.include_router(routes.router, prefix="/users", tags=["users"])

    async def init_db(self, engine):
        # optional DB init
        pass