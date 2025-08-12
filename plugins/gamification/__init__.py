from fastapi import APIRouter
import sys
import os


# Add the project root directory (adjust path as needed)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'app')))
print("PYTHONPATH inside plugin:", sys.path)

from core.plugin_loader import PluginBase

router = APIRouter(prefix="/gamification")

@router.get("/badges")
async def get_badges():
    return {"badges": ["Starter", "Pro", "Master"]}

class Plugin(PluginBase):
    def register_routes(self, app):
        app.include_router(router)
