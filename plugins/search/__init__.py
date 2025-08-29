from fastapi import FastAPI, APIRouter
from app.core.plugins.base import PluginBase, PluginConfig


class Config(PluginConfig):
    meili_url: str = "http://localhost:7700"
    meili_key: str | None = None


class Plugin(PluginBase):
    slug = "search"
    version = "0.1.0"
    dependencies: list[str] = ["products"]
    ConfigModel = Config

    def __init__(self, config: Config | None = None):
        super().__init__(config=config)
        self.router = APIRouter()

    def register_routes(self, app: FastAPI):
        from plugins.search.routes import router as search_router
        self.router.include_router(
            search_router,
            prefix=f"/{self.slug}",
            tags=["Search"],
        )
        app.include_router(self.router)

    async def init_db(self, engine):
        from plugins.search.models import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


