from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    yield

# plugins/cart/__init__.py
from fastapi import FastAPI, APIRouter
from app.core.plugins.base import PluginBase, PluginConfig

class Config(PluginConfig):
    """Configuration for Cart plugin"""
    max_items_per_cart: int = 50
    enable_cart_expiry: bool = True
    cart_expiry_minutes: int = 120

class Plugin(PluginBase):
    slug = "cart"
    version = "0.1.0"
    dependencies: list[str] = []
    ConfigModel = Config

    def __init__(self, config: Config | None = None):
        super().__init__(config=config)
        self.router = APIRouter()

    # Register routes
    def register_routes(self, app: FastAPI):
        try:
            from plugins.cart.routes import router as cart_router
            self.router.include_router(
                cart_router,
                prefix=f"/{self.slug}",
                tags=["Cart"]
            )
            app.include_router(self.router)
        except Exception as e:
            import traceback
            print(f"[{self.slug}] ❌ Failed to register routes: {e}")
            traceback.print_exc()

    # Startup / shutdown events
    def register_events(self, app: FastAPI):
        
        async def startup():
            print(f"[{self.slug}] plugin ready with config:", self.config.dict())

        
        async def shutdown():
            print(f"[{self.slug}] plugin shutting down")

    # Optional DB initialization
    async def init_db(self, engine):
        try:
            # Could create default carts or run migrations
            pass
        except Exception as e:
            import traceback
            print(f"[{self.slug}] ❌ DB init failed: {e}")
            traceback.print_exc()