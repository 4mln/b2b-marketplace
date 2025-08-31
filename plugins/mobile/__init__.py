"""
Mobile API Optimization Plugin
Comprehensive mobile-optimized API functionality for the B2B marketplace
"""

from fastapi import FastAPI, APIRouter
from app.core.plugins.base import PluginBase, PluginConfig

# -----------------------------
# Plugin configuration schema
# -----------------------------
class Config(PluginConfig):
    """Config schema for Mobile API Optimization plugin"""
    enabled: bool = True
    enable_compression: bool = True
    enable_caching: bool = True
    cache_ttl_seconds: int = 300
    max_cache_size_mb: int = 100
    enable_offline_support: bool = True
    max_offline_queue_size: int = 1000
    enable_performance_tracking: bool = True
    enable_push_notifications: bool = True
    enable_feature_flags: bool = True
    enable_sync: bool = True

# -----------------------------
# Plugin class
# -----------------------------
class Plugin(PluginBase):
    slug = "mobile"
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
            tags=["Mobile API Optimization"]
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
        # Optional async DB initialization for mobile tables
        if self.config.enable_performance_tracking:
            print(f"[{self.slug}] DB initialization completed (placeholder)")

__all__ = ["Plugin", "Config", "router"]


