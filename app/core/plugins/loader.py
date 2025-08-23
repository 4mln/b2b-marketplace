from __future__ import annotations
import asyncio
import importlib
import os
import pkgutil
import sys
from typing import Dict, List, Tuple, Type
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from pydantic import BaseModel

from .base import PluginBase, PluginConfig
from .registry import PluginRegistry

class LoaderSettings(BaseModel):
    plugins_package: str = "plugins"  # Python package name
    plugins_fs_path: str | None = None # filesystem path; if None, resolved via package
    enable_hot_reload: bool = False

class PluginLoader:
    """Advanced plugin loader with dependency resolution and conflict detection."""

    def __init__(self, settings: LoaderSettings | None = None) -> None:
        self.settings = settings or LoaderSettings()
        self.registry = PluginRegistry()
        self._discovered: Dict[str, str] = {}  # slug -> module_name

    # ===== Discovery =====
    def discover(self) -> Dict[str, str]:
        package = self.settings.plugins_package
        fs_path = self.settings.plugins_fs_path

        if fs_path is None:
            # Try to import the package to discover path
            pkg = importlib.import_module(package)
            pkg_path = os.path.dirname(pkg.__file__)  # type: ignore[attr-defined]
        else:
            pkg_path = fs_path

        if not os.path.isdir(pkg_path):
            raise RuntimeError(f"Plugins path does not exist: {pkg_path}")

        discovered: Dict[str, str] = {}
        for _, name, ispkg in pkgutil.iter_modules([pkg_path]):
            if not ispkg:
                continue
            module_name = f"{package}.{name}"
            try:
                mod = importlib.import_module(module_name)
                plugin_class: Type[PluginBase] | None = getattr(mod, "Plugin", None)
                if not plugin_class:
                    continue
                # Instantiate once to read slug
                instance = plugin_class()
                slug = instance.slug or name
                discovered[slug] = module_name
            except Exception as e:
                print(f"[discover] Failed to import {module_name}: {e}")
        self._discovered = discovered
        return discovered

    # ===== Dependency resolution (topological sort) =====
    def _resolve_load_order(self) -> List[Tuple[str, str]]:
        # returns list of (slug, module_name)
        # Build graph
        graph: Dict[str, List[str]] = {}
        meta: Dict[str, List[str]] = {}
        # Preload dependencies from plugin classes
        for slug, module_name in self._discovered.items():
            mod = importlib.import_module(module_name)
            cls: Type[PluginBase] = getattr(mod, "Plugin")
            deps = list(getattr(cls, "dependencies", []) or [])
            graph[slug] = deps
            meta[slug] = deps

        # Kahn's algorithm
        incoming = {n: 0 for n in graph}
        for n in graph:
            for d in graph[n]:
                if d not in incoming:
                    incoming[d] = 0
                incoming[d] += 1
        order: List[str] = []
        queue = [n for n, deg in incoming.items() if deg == 0]
        while queue:
            n = queue.pop(0)
            if n in graph:
                order.append(n)
                for m in graph[n]:
                    incoming[m] -= 1
                    if incoming[m] == 0:
                        queue.append(m)
        # Detect unresolved cycles or missing deps
        if len(order) < len(graph):
            unresolved = set(graph.keys()) - set(order)
            raise RuntimeError(f"Dependency cycle or missing plugin(s): {sorted(unresolved)}. Graph={meta}")
        return [(slug, self._discovered[slug]) for slug in order if slug in self._discovered]

    # ===== Loading =====
    async def load_all(self, app: FastAPI, engine: AsyncEngine) -> List[PluginBase]:
        if not self._discovered:
            self.discover()
        order = self._resolve_load_order()
        loaded: List[PluginBase] = []
        for slug, module_name in order:
            try:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                mod = importlib.import_module(module_name)
                cls: Type[PluginBase] = getattr(mod, "Plugin")

                # Provide per-plugin config via app.state if present
                config_map = getattr(app.state, "plugin_config", {})
                cfg_model = getattr(cls, "ConfigModel", PluginConfig)
                cfg_data = config_map.get(slug, {}) if isinstance(config_map, dict) else {}
                config = cfg_model(**cfg_data) if isinstance(cfg_data, dict) else cfg_model()

                instance = cls(config=config)
                if not instance.config.enabled:
                    print(f"[loader] Skip disabled plugin '{slug}'")
                    continue

                # Register to registry first (so others can reference it)
                self.registry.add(instance)

                # Dry-run register into temp app for route conflict detection
                temp_app = FastAPI()
                instance.register_routes(temp_app)
                for route in temp_app.routes:
                    self.registry.claim_route(route.path, slug)

                # Real registration
                instance.register_routes(app)

                # DB and hooks
                await instance.init_db(engine)
                await instance.on_startup(app)

                loaded.append(instance)
                print(f"[loader] Loaded plugin: {slug} ({instance.version})")
            except Exception as e:
                print(f"[loader] Failed to load '{slug}' from {module_name}: {e}")
        # store registry on app for admin endpoints
        app.state.plugin_registry = self.registry
        app.state.plugins = loaded
        return loaded

    async def shutdown_all(self, app: FastAPI) -> None:
        for p in getattr(app.state, "plugins", []) or []:
            try:
                await p.on_shutdown(app)
            except Exception as e:
                print(f"[loader] Shutdown error for '{p.slug}': {e}")

    # ===== Optional: naive hot-reload for dev =====
    def enable_hot_reload(self, app: FastAPI, engine: AsyncEngine, interval_sec: float = 2.0) -> None:
        if not self.settings.enable_hot_reload:
            return
        async def watcher():
            last_snapshot: Dict[str, float] = {}
            pkg = importlib.import_module(self.settings.plugins_package)
            pkg_path = os.path.dirname(pkg.__file__)
            while True:
                changed = False
                for root, _, files in os.walk(pkg_path):
                    for f in files:
                        if f.endswith('.py'):
                            p = os.path.join(root, f)
                            mtime = os.path.getmtime(p)
                            if p not in last_snapshot:
                                last_snapshot[p] = mtime
                            elif last_snapshot[p] != mtime:
                                last_snapshot[p] = mtime
                                changed = True
                if changed:
                    print('[hot-reload] Change detected, reloading plugins...')
                    # naive approach: hard reset registry and reload all
                    self.registry = PluginRegistry()
                    self._discovered.clear()
                    await self.shutdown_all(app)
                    await self.load_all(app, engine)
                await asyncio.sleep(interval_sec)
        # fire and forget
        asyncio.create_task(watcher())