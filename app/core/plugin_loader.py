# app/core/plugin_loader.py
import importlib
import os
import pkgutil
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from typing import List, Union

# Base class for plugins
class PluginBase:
    def register_routes(self, app: FastAPI):
        raise NotImplementedError

    async def init_db(self, engine: AsyncEngine):
        pass

    async def shutdown(self):
        pass

# Path to 'plugins' folder
PLUGIN_FOLDER_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "plugins")
)

# Which plugins are active
ACTIVE_PLUGINS = {
    "gamification": True,
    "seller": True,
    "test_connections": True,
    "user": True,
    "auth": True,
}

def discover_plugins(plugin_folder: str = PLUGIN_FOLDER_PATH) -> List[PluginBase]:
    """Discover all class-based plugins in the plugins folder."""
    plugins = []

    print(f"🔍 Discovering plugins in: {plugin_folder}")
    if not os.path.isdir(plugin_folder):
        print(f"❌ Plugin folder not found: {plugin_folder}")
        return plugins

    for finder, name, ispkg in pkgutil.iter_modules([plugin_folder]):
        print(f"Found module: {name} (is package: {ispkg})")
        if not ispkg:
            continue
        if not ACTIVE_PLUGINS.get(name, True):
            print(f"⚠️ Plugin {name} is disabled in ACTIVE_PLUGINS")
            continue

        module_name = f"plugins.{name}"
        try:
            module = importlib.import_module(module_name)
            plugin_class = getattr(module, "Plugin", None)
            if plugin_class:
                plugin_instance = plugin_class()
                plugins.append(plugin_instance)
                print(f"✅ Loaded plugin: {name}")
            else:
                print(f"⚠️ No Plugin class found in {name}")
        except Exception as e:
            print(f"❌ Error loading plugin {name}: {e}")

    print(f"📌 Total plugins discovered: {[p.__class__.__name__ for p in plugins]}")
    return plugins


async def load_plugins(app: FastAPI, engine: AsyncEngine) -> List[PluginBase]:
    """Register routes and initialize DB for discovered plugins."""
    plugins = discover_plugins()
    for plugin in plugins:
        try:
            plugin.register_routes(app)
            print(f"🔌 Routes registered for plugin: {plugin.__class__.__name__}")
        except Exception as e:
            print(f"❌ Failed to register routes for {plugin.__class__.__name__}: {e}")

        if hasattr(plugin, "init_db"):
            try:
                await plugin.init_db(engine)
                print(f"💾 DB initialized for plugin: {plugin.__class__.__name__}")
            except Exception as e:
                print(f"❌ DB init failed for {plugin.__class__.__name__}: {e}")

    print(f"📌 Total plugins loaded: {[p.__class__.__name__ for p in plugins]}")
    return plugins