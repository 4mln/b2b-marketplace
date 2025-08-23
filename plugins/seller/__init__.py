from fastapi import APIRouter, FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.plugins.base import PluginBase, PluginConfig

router = APIRouter()

@router.get("/")
async def list_sellers():
    return {"sellers": []}

class SellerConfig(PluginConfig):
    # example toggleable flags
    onboarding_required: bool = True

class Plugin(PluginBase):
    name = "Seller Management"
    slug = "seller"
    version = "0.1.0"
    description = "Core seller workflows"
    author = "b2b-team"
    dependencies = []

    ConfigModel = SellerConfig

    def register_routes(self, app: FastAPI) -> None:
        super().register_routes(app)
        app.include_router(router, prefix=f"/{self.slug}", tags=[self.name])

    async def init_db(self, engine: AsyncEngine) -> None:
        # TODO: integrate plugin-specific models/migrations here
        return None