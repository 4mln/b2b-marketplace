# plugins/user/__init__.py
from fastapi import FastAPI, APIRouter
from app.core.plugins.base import PluginBase, PluginConfig


class Config(PluginConfig):
    """Config schema for User plugin"""
    max_users: int = 5000
    enable_email_verification: bool = True
    enable_2fa: bool = False


class Plugin(PluginBase):
    slug = "user"
    version = "0.1.0"
    dependencies: list[str] = []
    ConfigModel = Config

    def __init__(self, config: Config | None = None):
        super().__init__(config=config)

        from plugins.user.routes import router as user_router

        self.router = APIRouter()
        self.router.include_router(
            user_router,
            prefix=f"/{self.slug}",
            tags=["User"]
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
        # Optional async DB initialization
        pass