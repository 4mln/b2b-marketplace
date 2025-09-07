from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    yield

from fastapi import FastAPI, APIRouter
from app.core.plugins.base import PluginBase, PluginConfig


class Config(PluginConfig):
    default_locale: str = "fa"


class Plugin(PluginBase):
    slug = "i18n"
    version = "0.1.0"
    dependencies: list[str] = []
    ConfigModel = Config

    def __init__(self, config: Config | None = None):
        super().__init__(config=config)
        self.router = APIRouter()

    def register_routes(self, app: FastAPI):
        from plugins.i18n.routes import router as i18n_router
        self.router.include_router(i18n_router, prefix=f"/{self.slug}", tags=["i18n"])
        app.include_router(self.router)











