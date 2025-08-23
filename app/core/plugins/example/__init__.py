from fastapi import APIRouter, FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.plugins.base import PluginBase, PluginConfig

router = APIRouter()

@router.get("/")
async def ping_example():
    return {"ok": True, "plugin": "example"}

class ExampleConfig(PluginConfig):
    greeting: str = "hello"

class Plugin(PluginBase):
    name = "Example Plugin"
    slug = "example"
    version = "1.0.0"
    description = "Demonstration plugin"
    author = "Core Team"
    dependencies = []  # e.g., ["auth"]

    ConfigModel = ExampleConfig

    def register_routes(self, app: FastAPI) -> None:
        super().register_routes(app)
        app.include_router(router, prefix=f"/{self.slug}", tags=[self.name])

    async def init_db(self, engine: AsyncEngine) -> None:
        # create tables or seed if needed
        return None

    async def on_startup(self, app: FastAPI) -> None:
        print(f"[{self.slug}] startup; config.greeting={self.config.greeting}")

    async def on_shutdown(self, app: FastAPI) -> None:
        print(f"[{self.slug}] shutdown")