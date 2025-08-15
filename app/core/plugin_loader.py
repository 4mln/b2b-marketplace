import importlib
import os
import pkgutil
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from typing import List

class PluginBase:
    """
    Base class plugins should inherit from.
    Plugins must implement:
    - register_routes(app: FastAPI)
    - init_db(engine: AsyncEngine)
    - shutdown()  # optional
    """
    def register_routes(self, app: FastAPI):
        raise NotImplementedError

    async def init_db(self, engine: AsyncEngine):
        pass

    async def shutdown(self):
        pass


# Absolute path to your root-level 'plugins' folder
PLUGIN_FOLDER_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "plugins")
)

# === New: control which plugins are active ===
ACTIVE_PLUGINS = {
    "gamification": True,
    "test_connections": True,  # Set False in production
}


def discover_plugins(plugin_folder: str = PLUGIN_FOLDER_PATH) -> List[PluginBase]:
    """
    Discover and import all plugins in the root 'plugins' folder.
    Expects each plugin folder to have an __init__.py with a Plugin class.
    """
    plugins = []

    if not os.path.isdir(plugin_folder):
        print(f"Plugin folder not found: {plugin_folder}")
        return plugins

    for finder, name, ispkg in pkgutil.iter_modules([plugin_folder]):
        if not ispkg:
            continue

        # Skip plugins marked as inactive
        if not ACTIVE_PLUGINS.get(name, True):
            print(f"Plugin {name} is disabled, skipping")
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
                print(f"No Plugin class found in {module_name}")
        except Exception as e:
            print(f"⚠️ Error loading plugin {name}: {e}")

    return plugins


async def load_plugins(app: FastAPI, engine: AsyncEngine):
    """
    Load all plugins, register their routes, and initialize DB.
    """
    plugins = discover_plugins()
    for plugin in plugins:
        plugin.register_routes(app)
        await plugin.init_db(engine)

    return plugins