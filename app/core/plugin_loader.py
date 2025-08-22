import importlib
import pkgutil
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from typing import List

# Base class for plugins
class PluginBase:
    def register_routes(self, app: FastAPI):
        pass

    async def init_db(self, engine: AsyncEngine):
        pass


async def load_plugins(app: FastAPI, engine: AsyncEngine) -> List[PluginBase]:
    plugins = []
    discovered_path = "plugins"

    for finder, name, ispkg in pkgutil.iter_modules([discovered_path]):
        full_module_name = f"{discovered_path}.{name}"
        try:
            module = importlib.import_module(full_module_name)
            plugin_class = getattr(module, "Plugin", None)
            if plugin_class:
                plugin_instance = plugin_class()
                # register routes
                plugin_instance.register_routes(app)
                # initialize DB
                await plugin_instance.init_db(engine)
                plugins.append(plugin_instance)
                print(f"✅ Loaded plugin: {name}")
        except Exception as e:
            print(f"❌ Error loading plugin {name}: {e}")
    return plugins