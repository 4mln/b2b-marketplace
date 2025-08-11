from fastapi import APIRouter
from core.plugin_loader import PluginBase  # if plugin_loader.py is inside core/
# OR
from plugin_loader import PluginBase       # if plugin_loader.py is in project root and app root is a package

router = APIRouter(prefix="/gamification")

@router.get("/badges")
async def get_badges():
    return {"badges": ["Starter", "Pro", "Master"]}

class Plugin(PluginBase):
    def register_routes(self, app):
        app.include_router(router)