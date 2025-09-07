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
    """Config schema for Auth plugin"""
    token_expire_minutes: int = 60
    enable_2fa: bool = False
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"

# -----------------------------
# Plugin class
# -----------------------------
class Plugin(PluginBase):
    slug = "auth"
    version = "0.1.0"
    dependencies: list[str] = []
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
            tags=["Auth"]
        )
        app.include_router(self.router)

    # -----------------------------
    # Startup / shutdown events
    # -----------------------------
    def register_events(self, app: FastAPI):
        
        async def startup():
            print(f"[{self.slug}] plugin ready with config:", self.config.dict())

        
        async def shutdown():
            print(f"[{self.slug}] plugin shutting down")

    # -----------------------------
    # Optional async DB init
    # -----------------------------
    async def init_db(self, engine):
        pass