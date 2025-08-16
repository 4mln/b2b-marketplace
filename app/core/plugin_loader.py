# app/core/plugin_loader.py
import importlib
import os
import pkgutil
import asyncio

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from typing import List, Union

# Base class for plugins (optional)
class PluginBase:
    def register_routes(self, app: FastAPI):
        raise NotImplementedError

    async def init_db(self, engine: AsyncEngine):
        pass

    async def shutdown(self):
        pass


# Absolute path to the 'plugins' folder
PLUGIN_FOLDER_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "plugins")
)

# Active plugins control
ACTIVE_PLUGINS = {
    "gamification": True,
    "seller": True,
    "test_connections": True,
    "user": True,
    "auth": True,
}

def discover_plugins(plugin_folder: str = PLUGIN_FOLDER_PATH) -> List[Union[PluginBase, callable]]:
    """
    Discover all plugins in the 'plugins' folder.
    Can be class-based (Plugin) or async function (register).
    """
    plugins = []

    if not os.path.isdir(plugin_folder):
        print(f"Plugin folder not found: {plugin_folder}")
        return plugins

    for finder, name, ispkg in pkgutil.iter_modules([plugin_folder]):
        if not ispkg or not ACTIVE_PLUGINS.get(name, True):
            continue

        module_name = f"plugins.{name}"
        try:
            module = importlib.import_module(module_name)

            # First, look for class-based Plugin
            plugin_class = getattr(module, "Plugin", None)
            if plugin_class:
                plugin_instance = plugin_class()
                plugins.append(plugin_instance)
                print(f"✅ Loaded class-based plugin: {name}")
                continue

            # Fallback: look for async register function
            register_func = getattr(module, "register", None)
            if register_func:
                plugins.append(register_func)
                print(f"✅ Loaded function-based plugin: {name}")
                continue

            print(f"⚠️ No Plugin class or register function found in {name}")
        except Exception as e:
            print(f"⚠️ Error loading plugin {name}: {e}")

    return plugins


async def load_plugins(app: FastAPI, engine: AsyncEngine):
    """
    Load all plugins: register routes and init DB.
    Supports both class-based and function-based plugins.
    """
    plugins = discover_plugins()
    for plugin in plugins:
        # Class-based plugin
        if hasattr(plugin, "register_routes"):
            plugin.register_routes(app)
            print(f"🔌 Plugin {plugin.__class__.__name__} registered with register_routes")

        # Function-based plugin
        elif callable(plugin):
            await plugin(app, engine)
            print(f"🔌 Function plugin {plugin.__name__} executed")

        # Init DB if available
        if hasattr(plugin, "init_db"):
            await plugin.init_db(engine)
            print(f"💾 Plugin {plugin.__class__.__name__} DB initialized")

    return plugins
