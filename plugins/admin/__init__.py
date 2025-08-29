from fastapi import FastAPI, APIRouter
from app.core.plugins.base import PluginBase, PluginConfig


class Config(PluginConfig):
    pass


class Plugin(PluginBase):
    slug = "admin"
    version = "0.1.0"
    dependencies: list[str] = ["guilds", "products", "rfq", "ads"]
    ConfigModel = Config

    def __init__(self, config: Config | None = None):
        super().__init__(config=config)
        self.router = APIRouter()

    def register_routes(self, app: FastAPI):
        from plugins.admin.routes import router as admin_router
        self.router.include_router(
            admin_router,
            prefix=f"/{self.slug}",
            tags=["Admin"]
        )
        app.include_router(self.router)


