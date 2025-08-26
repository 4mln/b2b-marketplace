from fastapi import FastAPI, APIRouter
from app.core.plugins.base import PluginBase, PluginConfig

# -----------------------------
# Plugin configuration schema
# -----------------------------
class Config(PluginConfig):
    """Config schema for Advanced Features plugin"""
    enabled: bool = True
    enable_ai_assistant: bool = False
    ai_model: str = "gpt-4"
    experimental_features: list[str] = []

# -----------------------------
# Plugin class
# -----------------------------
class Plugin(PluginBase):
    slug = "advanced-features"
    version = "0.1.0"
    dependencies: list[str] = ["user", "analytics"]
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
        app.include_router(self.router, prefix=f"/{self.slug}", tags=["Advanced Features"])

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
    # Async DB init
    # -----------------------------
    async def init_db(self, engine):
        from . import crud
        await crud.init_tables(engine)
