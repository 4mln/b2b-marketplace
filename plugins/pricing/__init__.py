from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    yield

from fastapi import FastAPI, APIRouter
from app.core.plugins.base import PluginBase, PluginConfig
from typing import Optional
import logging

# -----------------------------
# Plugin configuration schema
# -----------------------------
class Config(PluginConfig):
    """Config schema for Pricing plugin"""
    enabled: bool = True
    default_currency: str = "USD"
    allow_discounts: bool = True
    max_discount_percent: float = 50.0
    log_level: str = "INFO"

# -----------------------------
# Plugin class
# -----------------------------
class Plugin(PluginBase):
    slug = "pricing"
    version = "0.1.0"
    dependencies: list[str] = ["products"]  # products plugin required
    ConfigModel = Config

    def __init__(self, config: Optional[Config] = None):
        super().__init__(config=config)
        from . import routes
        self.router = APIRouter()
        self.router.include_router(
            routes.router,
            prefix=f"/{self.slug}",
            tags=["Pricing"]
        )
        self.logger = logging.getLogger(self.slug)
        self.logger.setLevel(getattr(logging, self.config.log_level.upper(), logging.INFO))

    def register_routes(self, app: FastAPI):
        app.include_router(self.router)

    def register_events(self, app: FastAPI):
        
        async def startup():
            self.logger.info(f"[{self.slug}] plugin ready with config: {self.config.dict()}")

        
        async def shutdown():
            self.logger.info(f"[{self.slug}] plugin shutting down")

    async def init_db(self, engine):
        # Placeholder: Initialize pricing rules table if needed
        self.logger.info(f"[{self.slug}] DB init placeholder")