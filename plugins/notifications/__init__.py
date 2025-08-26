from fastapi import FastAPI, APIRouter
from app.core.plugins.base import PluginBase, PluginConfig
from typing import Optional
import logging

# -----------------------------
# Plugin configuration schema
# -----------------------------
class Config(PluginConfig):
    """Config schema for Notifications plugin"""
    enabled: bool = True
    email_enabled: bool = True
    in_app_enabled: bool = True
    smtp_server: str = "smtp.example.com"
    smtp_port: int = 587
    smtp_username: str = "user@example.com"
    smtp_password: str = "supersecret"
    default_sender: str = "noreply@example.com"
    log_level: str = "INFO"

# -----------------------------
# Plugin class
# -----------------------------
class Plugin(PluginBase):
    slug = "notifications"
    version = "0.1.0"
    dependencies: list[str] = ["user"]  # user plugin required
    ConfigModel = Config

    def __init__(self, config: Optional[Config] = None):
        super().__init__(config=config)
        from . import routes
        self.router = APIRouter()
        self.router.include_router(
            routes.router,
            prefix=f"/{self.slug}",
            tags=["Notifications"]
        )
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
        # Placeholder for DB initialization, e.g., notifications table
        self.logger.info(f"[{self.slug}] DB init placeholder")