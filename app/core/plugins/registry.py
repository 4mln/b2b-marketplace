from __future__ import annotations
from typing import Dict, List
from .base import PluginBase

class PluginRegistry:
    """In-memory registry of loaded plugins and their routes."""

    def __init__(self) -> None:
        self._plugins: Dict[str, PluginBase] = {}  # slug -> instance
        self._route_owner: Dict[str, str] = {}     # path -> slug

    # Plugins
    def add(self, plugin: PluginBase) -> None:
        self._plugins[plugin.slug] = plugin

    def get(self, slug: str) -> PluginBase | None:
        return self._plugins.get(slug)

    def list(self) -> List[PluginBase]:
        return list(self._plugins.values())

    # Routes
    def claim_route(self, path: str, slug: str) -> None:
        if path in self._route_owner and self._route_owner[path] != slug:
            owner = self._route_owner[path]
            raise RuntimeError(f"Route conflict on '{path}': already owned by '{owner}', cannot assign to '{slug}'")
        self._route_owner[path] = slug

    def routes(self) -> Dict[str, str]:
        return dict(self._route_owner)