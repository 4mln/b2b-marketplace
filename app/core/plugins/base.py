from __future__ import annotations
from typing import Optional, List, Dict, Any
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from pydantic import BaseModel

class PluginConfig(BaseModel):
    """Per-plugin configuration model. Extend inside plugin via subclassing."""
    enabled: bool = True

class PluginBase:
    """Base class for all plugins."""

    # Metadata (override in plugin)
    name: str = "Unnamed"
    slug: str = "unnamed"  # unique identifier used in paths, tags, registry keys
    version: str = "0.0.1"
    description: str = ""
    author: str = "Unknown"
    dependencies: List[str] = []  # list of plugin slugs this plugin depends on

    # Internal flags
    _routes_registered: bool = False

    # Optional: plugin-level config (override with your subclass of PluginConfig)
    ConfigModel = PluginConfig

    def __init__(self, config: Optional[PluginConfig] = None):
        self.config = config or self.ConfigModel()

    # ===== Life-cycle hooks =====
    def register_routes(self, app: FastAPI) -> None:
        """Attach FastAPI routers here. Must be idempotent."""
        if self._routes_registered:
            return
        self._routes_registered = True

    async def init_db(self, engine: AsyncEngine) -> None:
        """Async DB initialization (migrations/DDL/seed)."""
        return None

    async def on_startup(self, app: FastAPI) -> None:
        return None

    async def on_shutdown(self, app: FastAPI) -> None:
        return None

    # ===== Introspection helpers =====
    def export_metadata(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "slug": self.slug,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "dependencies": list(self.dependencies or []),
            "config": self.config.model_dump(),
        }