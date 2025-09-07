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
    """Config schema for Buyer plugin"""
    max_buyers: int = 1000
    enable_notifications: bool = True

# -----------------------------
# Plugin class
# -----------------------------
class Plugin(PluginBase):
    slug = "buyers"
    version = "0.1.0"
    dependencies: list[str] = []
    ConfigModel = Config

    def __init__(self, config: Config | None = None):
        super().__init__(config=config)
        # No router yet
        self.router: APIRouter | None = None

    # -----------------------------
    # Register routes to app
    # -----------------------------
    def register_routes(self, app: FastAPI):
        # Lazy import inside the method
        from . import routes  # <- THIS MUST BE EXACT: .routes
        # Directly reference the routes.router without re-adding prefix
        self.router = routes.router
        app.include_router(self.router)

    # -----------------------------
    # Register startup / shutdown events
    # -----------------------------
    def register_events(self, app: FastAPI):
        
        async def startup():
            print(f"[{self.slug}] plugin ready with config:", self.config.dict())

        
        async def shutdown():
            print(f"[{self.slug}] plugin shutting down")

    # -----------------------------
    # Optional async DB initialization
    # -----------------------------
    async def init_db(self, engine):
        pass