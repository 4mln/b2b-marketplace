from app.core.plugin_loader import PluginBase
from plugins.seller import routes

class Plugin(PluginBase):
    """Seller plugin"""

    def register_routes(self, app):
        app.include_router(routes.router, prefix="/sellers", tags=["sellers"])

    async def init_db(self, engine):
        # optional DB init
        pass