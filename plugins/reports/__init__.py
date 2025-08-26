# plugins/reports/__init__.py
from fastapi import FastAPI, APIRouter
from app.core.plugins.base import PluginBase, PluginConfig

class Config(PluginConfig):
    """Configuration for Reports plugin"""
    enable_order_reports: bool = True
    enable_user_reports: bool = True
    enable_sales_reports: bool = True

class Plugin(PluginBase):
    slug = "reports"
    version = "0.1.0"
    dependencies: list[str] = []
    ConfigModel = Config

    def __init__(self, config: Config | None = None):
        super().__init__(config=config)
        self.router = APIRouter()

    # Register routes
    def register_routes(self, app: FastAPI):
        try:
            from plugins.reports.routes import router as reports_router
            self.router.include_router(
                reports_router,
                prefix=f"/{self.slug}",
                tags=["Reports"]
            )
            app.include_router(self.router)
        except Exception as e:
            import traceback
            print(f"[{self.slug}] ❌ Failed to register routes: {e}")
            traceback.print_exc()

    # Startup / shutdown events
    def register_events(self, app: FastAPI):
        @app.on_event("startup")
        async def startup():
            print(f"[{self.slug}] plugin ready with config:", self.config.dict())

        @app.on_event("shutdown")
        async def shutdown():
            print(f"[{self.slug}] plugin shutting down")

    # Optional DB initialization
    async def init_db(self, engine):
        try:
            # Could create default report tables if needed
            pass
        except Exception as e:
            import traceback
            print(f"[{self.slug}] ❌ DB init failed: {e}")
            traceback.print_exc()
