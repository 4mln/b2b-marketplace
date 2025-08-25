from fastapi import FastAPI, APIRouter
from app.core.plugins.base import PluginBase, PluginConfig
from plugins.test_connections.routes import router as test_router  # ✅ moved import here


class Config(PluginConfig):
    enable_logging: bool = True


class Plugin(PluginBase):
    slug = "test_connections"
    version = "0.1.0"
    dependencies: list[str] = []
    ConfigModel = Config

    def __init__(self, config: Config | None = None):
        super().__init__(config=config)
        self.router = APIRouter()
        self.router.include_router(
            test_router,
            prefix=f"/{self.slug}",
            tags=["Test Connections"]
        )

    def register_routes(self, app: FastAPI):
        app.include_router(self.router)

    def register_events(self, app: FastAPI):
        @app.on_event("startup")
        async def startup():
            print(f"[{self.slug}] plugin ready with config:", self.config.dict())

        @app.on_event("shutdown")
        async def shutdown():
            print(f"[{self.slug}] plugin shutting down")

    async def init_db(self, engine):
        pass