from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health():
    return {"ok": True, "plugin": "seller"}
```

#### `plugins/buyer/__init__.py`
```python
from fastapi import APIRouter, FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.plugins.base import PluginBase, PluginConfig

router = APIRouter()

@router.get("/")
async def list_buyers():
    return {"buyers": []}

class BuyerConfig(PluginConfig):
    vip_enabled: bool = False

class Plugin(PluginBase):
    name = "Buyer Management"
    slug = "buyer"
    version = "0.1.0"
    description = "Core buyer workflows"
    author = "b2b-team"
    dependencies = []

    ConfigModel = BuyerConfig

    def register_routes(self, app: FastAPI) -> None:
        super().register_routes(app)
        app.include_router(router, prefix=f"/{self.slug}", tags=[self.name])

    async def init_db(self, engine: AsyncEngine) -> None:
        return None