from fastapi import FastAPI, APIRouter
from app.core.plugins.base import PluginBase, PluginConfig


class Config(PluginConfig):
    pass


class Plugin(PluginBase):
    slug = "escrow"
    version = "0.1.0"
    dependencies: list[str] = ["orders", "payments", "wallet"]
    ConfigModel = Config

    def __init__(self, config: Config | None = None):
        super().__init__(config=config)
        self.router = APIRouter()

    def register_routes(self, app: FastAPI):
        from plugins.escrow.routes import router as escrow_router
        self.router.include_router(escrow_router, prefix=f"/{self.slug}", tags=["Escrow"])
        app.include_router(self.router)

    async def init_db(self, engine):
        from plugins.escrow.models import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)












