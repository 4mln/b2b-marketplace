from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    yield

from .main import WalletPlugin as Plugin

__all__ = ["Plugin"]