from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    yield

"""
Advanced Search & Filters System Plugin
Comprehensive search capabilities for the B2B marketplace
"""

from fastapi import FastAPI, APIRouter
from app.core.plugins.base import PluginBase, PluginConfig

class Config(PluginConfig):
    pass

class Plugin(PluginBase):
    slug = "search"
    version = "0.1.0"
    dependencies: list[str] = ["auth"]
    ConfigModel = Config

    def __init__(self, config: Config | None = None):
        super().__init__(config=config)
        self.router = APIRouter()

    def register_routes(self, app: FastAPI):
        from . import routes  # Lazy import
        self.router.include_router(routes.router, prefix=f"/{self.slug}", tags=["Search"])
        app.include_router(self.router)

    async def init_db(self, engine):
        # Tables are created by Alembic migrations
        pass

__all__ = ["Plugin"]







