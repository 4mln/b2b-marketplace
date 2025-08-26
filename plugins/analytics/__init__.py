from fastapi import FastAPI, APIRouter
from app.core.plugins.base import PluginBase, PluginConfig
from typing import Optional
import logging

# -----------------------------
# Plugin configuration schema
# -----------------------------
class Config(PluginConfig):
    """Config schema for Analytics plugin"""
    enabled: bool = True
    track_user_activity: bool = True
    max_events_per_minute: int = 1000
    log_level: str = "INFO"  # production-ready logging level

# -----------------------------
# Plugin class
# -----------------------------
class Plugin(PluginBase):
    slug = "analytics"
    version = "0.1.0"
    dependencies: list[str] = ["user"]  # depends on user plugin
    ConfigModel = Config

    def __init__(self, config: Optional[Config] = None):
        super().__init__(config=config)
        self.router = APIRouter()
        from . import routes
        self.router.include_router(
            routes.router,
            prefix=f"/{self.slug}",
            tags=["Analytics"]
        )
        # Configure plugin logger
        self.logger = logging.getLogger(self.slug)
        self.logger.setLevel(getattr(logging, self.config.log_level.upper(), logging.INFO))

    def register_routes(self, app: FastAPI):
        app.include_router(self.router)

    def register_events(self, app: FastAPI):
        @app.on_event("startup")
        async def startup():
            self.logger.info(f"[{self.slug}] plugin ready with config: {self.config.dict()}")

        @app.on_event("shutdown")
        async def shutdown():
            self.logger.info(f"[{self.slug}] plugin shutting down")

    async def init_db(self, engine):
        # Optional async DB initialization for analytics tables
        if self.config.track_user_activity:
            # Example: create tables if not exists (use Alembic in production)
            self.logger.info(f"[{self.slug}] DB initialization completed (placeholder)")