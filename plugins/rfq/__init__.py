from fastapi import FastAPI, APIRouter
from app.core.plugins.base import PluginBase, PluginConfig


class Config(PluginConfig):
    pass


class Plugin(PluginBase):
    slug = "rfq"
    version = "0.1.0"
    dependencies: list[str] = ["users", "products", "sellers"]
    ConfigModel = Config

    def __init__(self, config: Config | None = None):
        super().__init__(config=config)
        self.router = APIRouter()

    def register_routes(self, app: FastAPI):
        from plugins.rfq.routes import router as rfq_router
        self.router.include_router(
            rfq_router,
            prefix=f"/{self.slug}",
            tags=["RFQ"]
        )
        app.include_router(self.router)

    async def init_db(self, engine):
        from plugins.rfq.models import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)








