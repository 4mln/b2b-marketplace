"""
Analytics & Reporting System Plugin
Comprehensive business intelligence and reporting for the B2B marketplace
"""

from fastapi import FastAPI, APIRouter
from app.core.plugins.base import PluginBase, PluginConfig

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
    dependencies: list[str] = ["auth"]  # depends on auth plugin
    ConfigModel = Config

    def __init__(self, config: Config | None = None):
        super().__init__(config=config)
        self.router: APIRouter | None = None

    # -----------------------------
    # Lazy route registration
    # -----------------------------
    def register_routes(self, app: FastAPI):
        from . import routes  # relative import for lazy loading
        self.router = APIRouter()
        self.router.include_router(
            routes.router,
            prefix=f"/{self.slug}",
            tags=["Analytics"]
        )
        app.include_router(self.router)

    # -----------------------------
    # Startup / shutdown events
    # -----------------------------
    def register_events(self, app: FastAPI):
        @app.on_event("startup")
        async def startup():
            print(f"[{self.slug}] plugin ready with config:", self.config.dict())

        @app.on_event("shutdown")
        async def shutdown():
            print(f"[{self.slug}] plugin shutting down")

    # -----------------------------
    # Optional async DB init
    # -----------------------------
    async def init_db(self, engine):
        # Optional async DB initialization for analytics tables
        if self.config.track_user_activity:
            # Example: create tables if not exists (use Alembic in production)
            print(f"[{self.slug}] DB initialization completed (placeholder)")

__all__ = ["Plugin", "Config", "router"]