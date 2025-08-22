from app.core.plugin_loader import PluginBase
from plugins.test_connections import routes

class Plugin(PluginBase):
    """Test Connections plugin"""

    def register_routes(self, app):
        app.include_router(routes.router, prefix="/connections", tags=["connections"])

    async def init_db(self, engine):
        # optional DB init
        pass