from fastapi import FastAPI, APIRouter
from app.core.plugins.base import PluginBase, PluginConfig


class Config(PluginConfig):
    """Config schema for Seller plugin"""
    max_sellers: int = 500
    enable_notifications: bool = True


class Plugin(PluginBase):
    slug = "seller"
    version = "0.1.0"
    dependencies: list[str] = []
    ConfigModel = Config

    def __init__(self, config: Config | None = None):
        super().__init__(config=config)
        self.router = APIRouter()

    def register_routes(self, app: FastAPI):
        # ✅ Lazy import inside method to avoid early import issues
        from plugins.seller.routes import router as seller_router
        self.router.include_router(
            seller_router,
            prefix=f"/{self.slug}",
            tags=["Seller"]
        )
        app.include_router(self.router)

    def register_events(self, app: FastAPI):
        @app.on_event("startup")
        async def startup():
            print(f"[{self.slug}] plugin ready with config:", self.config.dict())

        @app.on_event("shutdown")
        async def shutdown():
            print(f"[{self.slug}] plugin shutting down")

    async def init_db(self, engine):
        # Optional async DB initialization
        pass