from app.core.plugin_loader import PluginBase
from plugins.buyer import routes

class Plugin(PluginBase):
    """Buyer plugin"""

    def register_routes(self, app):
        app.include_router(routes.router, prefix="/buyers", tags=["buyers"])

    async def init_db(self, engine):
        # optional DB init
        pass