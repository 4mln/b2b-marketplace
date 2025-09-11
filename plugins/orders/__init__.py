from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    yield

from fastapi import FastAPI, APIRouter
from app.core.plugins.base import PluginBase, PluginConfig
from app.db.base import Base

class Config(PluginConfig):
    """Config schema for Orders plugin"""
    max_orders_per_user: int = 100
    enable_notifications: bool = True

class Plugin(PluginBase):
    slug = "orders"
    version = "0.1.0"
    dependencies: list[str] = ["user", "products", "buyer", "seller"]  # core plugins
    ConfigModel = Config

    def __init__(self, config: Config | None = None):
        super().__init__(config=config)
        self.router = APIRouter()

    def register_routes(self, app: FastAPI):
        # 1️⃣ Remove previous routes from this plugin, if any
        app.router.routes = [
        r for r in app.router.routes 
        if getattr(r, "tags", None) != ["Orders"]
        ]

        from plugins.orders.routes import router as orders_router
        self.router.include_router(
            orders_router,
            prefix=f"/api/v1/{self.slug}",
            tags=["Orders"]
        )
        app.include_router(self.router)

    def register_events(self, app: FastAPI):
        
        async def startup():
            print(f"[{self.slug}] plugin ready with config:", self.config.dict())

        
        async def shutdown():
            print(f"[{self.slug}] plugin shutting down")

    async def init_db(self, engine):
         async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)