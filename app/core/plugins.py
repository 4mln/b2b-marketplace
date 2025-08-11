import importlib
import os
from fastapi import FastAPI

PLUGIN_FOLDER = os.path.join(os.path.dirname(__file__), "..", "plugins")

async def load_plugins(app: FastAPI):
    """
    Dynamically import and register plugins from plugins/ folder.
    Each plugin should have a `register_plugin(app)` async function.
    """
    for entry in os.listdir(PLUGIN_FOLDER):
        plugin_path = os.path.join(PLUGIN_FOLDER, entry)
        if os.path.isdir(plugin_path) and not entry.startswith("__"):
            module_name = f"app.plugins.{entry}.main"
            try:
                plugin_module = importlib.import_module(module_name)
                if hasattr(plugin_module, "register_plugin"):
                    await plugin_module.register_plugin(app)
                    print(f"Loaded plugin: {entry}")
            except Exception as e:
                print(f"Failed to load plugin {entry}: {e}")
