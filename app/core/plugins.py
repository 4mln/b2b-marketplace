import asyncio
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

def discover_plugins(plugin_folder: str = PLUGIN_FOLDER_PATH) -> List[PluginBase]:
    """
    Discover and import all plugins in the root 'plugins' folder.
    Expects each plugin folder to have an __init__.py with a Plugin class.
    """
    plugins = []

    # Ensure the plugin_folder exists
    if not os.path.isdir(plugin_folder):
        print(f"Plugin folder not found: {plugin_folder}")
        return plugins

    for finder, name, ispkg in pkgutil.iter_modules([plugin_folder]):
        if not ispkg:
            continue

        # Import path: since plugins folder is root-level, import as 'plugins.{name}'
        module_name = f"plugins.{name}"
        try:
            module = importlib.import_module(module_name)
            plugin_class = getattr(module, "Plugin", None)
            if plugin_class:
                plugin_instance = plugin_class()
                plugins.append(plugin_instance)
                print(f"Loaded plugin: {name}")
            else:
                print(f"No Plugin class found in {module_name}")
        except Exception as e:
            print(f"Error loading plugin {name}: {e}")

    return plugins

async def load_plugins(app: FastAPI, engine: AsyncEngine) -> list:
    """
    Load all plugins: register routes and initialize DB.
    Supports:
    - Plugin class with `register_routes(app)` (sync)
    - Plugin class with async `register(app, engine)`
    - Module-level async `register(app, engine)` function
    """
    plugins = discover_plugins()
    for plugin in plugins:
        # Case 1: Plugin class with sync register_routes
        if hasattr(plugin, "register_routes"):
            plugin.register_routes(app)
            print(f"🔌 Plugin {plugin.__class__.__name__} registered with register_routes")

        # Case 2: Plugin class with async register method
        elif hasattr(plugin, "register") and callable(getattr(plugin, "register")):
            method = getattr(plugin, "register")
            if asyncio.iscoroutinefunction(method):
                await method(app, engine)
            else:
                method(app, engine)
            print(f"🔌 Plugin {plugin.__class__.__name__} registered with async register")

        # Case 3: Module-level async `register` function
        elif hasattr(plugin, "register") and asyncio.iscoroutinefunction(plugin.register):
            await plugin.register(app, engine)
            print(f"🔌 Plugin {plugin.__name__} module-level register called")

        else:
            print(f"⚠️ Plugin {plugin.__class__.__name__} has no register function")

        # Initialize DB if defined
        if hasattr(plugin, "init_db") and asyncio.iscoroutinefunction(plugin.init_db):
            await plugin.init_db(engine)
            print(f"💾 Plugin {plugin.__class__.__name__} DB initialized")

    return plugins