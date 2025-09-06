from fastapi import FastAPI, APIRouter
from app.core.plugins.base import PluginBase, PluginConfig

class Config(PluginConfig):
    max_products_per_seller: int = 1000
    enable_notifications: bool = True

class Plugin(PluginBase):
    slug = "products"
    version = "0.1.0"
    dependencies: list[str] = ["users", "sellers"]
    ConfigModel = Config

    def __init__(self, config: Config | None = None):
        super().__init__(config=config)
        self.router = APIRouter()

    def register_routes(self, app: FastAPI):
        from . import routes  # Lazy import with relative path
        self.router.include_router(
            routes.router,
            prefix=f"/api/v1/{self.slug}",
            tags=["Products"]
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
        # Tables are created by Alembic migrations
        pass
