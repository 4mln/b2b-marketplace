from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    yield

from fastapi import FastAPI, APIRouter
from app.core.plugins.base import PluginBase, PluginConfig

# -----------------------------
# Plugin configuration schema
# -----------------------------
class Config(PluginConfig):
    """Config schema for Payments plugin"""
    enabled: bool = True
    provider: str = "stripe"  # default payment provider
    currency: str = "USD"

# -----------------------------
# Plugin class
# -----------------------------
class Plugin(PluginBase):
    slug = "payments"
    version = "0.1.0"
    dependencies: list[str] = ["user", "orders"]
    ConfigModel = Config

    def __init__(self, config: Config | None = None):
        super().__init__(config=config)
        self.router: APIRouter | None = None

    # -----------------------------
    # Route registration
    # -----------------------------
    def register_routes(self, app: FastAPI):
        from . import routes  # lazy import
        self.router = routes.router
        app.include_router(self.router, prefix=f"/{self.slug}", tags=["Payments"])

    # -----------------------------
    # Startup / shutdown events
    # -----------------------------
    def register_events(self, app: FastAPI):
        
        async def startup():
            print(f"[{self.slug}] plugin ready with config:", self.config.dict())

        
        async def shutdown():
            print(f"[{self.slug}] plugin shutting down")

    # -----------------------------
    # Async DB init
    # -----------------------------
    async def init_db(self, engine):
        from . import crud
        await crud.init_tables(engine)