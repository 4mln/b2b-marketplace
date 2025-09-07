from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    yield

from fastapi import FastAPI, APIRouter
from app.core.plugins.base import PluginBase, PluginConfig


class Config(PluginConfig):
    pass


class Plugin(PluginBase):
    slug = "guilds"
    version = "0.1.0"
    dependencies: list[str] = []
    ConfigModel = Config

    def __init__(self, config: Config | None = None):
        super().__init__(config=config)
        self.router = APIRouter()

    def register_routes(self, app: FastAPI):
        from plugins.guilds.routes import router as guilds_router
        self.router.include_router(
            guilds_router,
            prefix=f"/{self.slug}",
            tags=["Guilds"],
        )
        app.include_router(self.router)

    async def init_db(self, engine):
        from plugins.guilds.models import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


