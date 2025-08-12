import sys
sys.path.insert(0, '/code')

try:
    from app.core.plugin_loader import PluginBase
    print("+++ Successfully imported PluginBase")
except Exception as e:
    print(f"!!! Import error: {e}")
    raise

from fastapi import APIRouter

router = APIRouter(prefix="/gamification")

@router.get("/badges")
async def get_badges():
    return {"badges": ["Starter", "Pro", "Master"]}

class Plugin(PluginBase):
    def register_routes(self, app):
        app.include_router(router)
