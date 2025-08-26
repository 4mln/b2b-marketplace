from fastapi import FastAPI, APIRouter
from app.core.plugins.base import PluginBase, PluginConfig

class Config(PluginConfig):
    """Config schema for Subscriptions plugin"""
    max_subscription_plans: int = 10
    enable_notifications: bool = True

class Plugin(PluginBase):
    slug = "subscriptions"
    version = "0.1.0"
    dependencies: list[str] = ["users", "payments"]  # core plugins
    ConfigModel = Config

    def __init__(self, config: Config | None = None):
        super().__init__(config=config)
        self.router = APIRouter()

    def register_routes(self, app: FastAPI):
        # Remove previous routes if any
        app.router.routes = [
            r for r in app.router.routes if getattr(r, "tags", None) != ["Subscriptions"]
        ]

        from plugins.subscriptions.routes import router as subscriptions_router
        self.router.include_router(
            subscriptions_router,
            prefix=f"/{self.slug}",
            tags=["Subscriptions"]
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
        from plugins.subscriptions.models import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)