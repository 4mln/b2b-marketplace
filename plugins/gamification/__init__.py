# plugins/gamification/__init__.py
from fastapi import FastAPI, APIRouter
from app.core.plugins.base import PluginBase, PluginConfig


class Config(PluginConfig):
    """Config schema for Gamification plugin"""
    enable_points: bool = True
    enable_badges: bool = True
    default_points_per_action: int = 10
    max_badges_per_user: int = 50


class Plugin(PluginBase):
    slug = "gamification"
    version = "0.1.0"
    dependencies: list[str] = []
    ConfigModel = Config

    def __init__(self, config: Config | None = None):
        super().__init__(config=config)
        self.router = APIRouter()

    # -----------------------------
    # Register routes to app
    # -----------------------------
    def register_routes(self, app: FastAPI):
        try:
            from plugins.gamification.routes import router as gamification_router
            self.router.include_router(
                gamification_router,
                prefix=f"/{self.slug}",
                tags=["Gamification"]
            )
            app.include_router(self.router)
        except Exception as e:
            import traceback
            print(f"[{self.slug}] ❌ Failed to register routes: {e}")
            traceback.print_exc()

    # -----------------------------
    # Register startup / shutdown events
    # -----------------------------
    def register_events(self, app: FastAPI):
        @app.on_event("startup")
        async def startup():
            print(f"[{self.slug}] plugin ready with config:", self.config.dict())

        @app.on_event("shutdown")
        async def shutdown():
            print(f"[{self.slug}] plugin shutting down")

    # -----------------------------
    # Optional async DB initialization
    # -----------------------------
    async def init_db(self, engine):
        try:
            # Optional: initialize points/badges tables or default data
            pass
        except Exception as e:
            import traceback
            print(f"[{self.slug}] ❌ DB init failed: {e}")
            traceback.print_exc()