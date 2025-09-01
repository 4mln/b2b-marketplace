"""Test Plugin
A simple test plugin to verify plugin loading works
"""

from fastapi import FastAPI, APIRouter
from app.core.plugins.base import PluginBase, PluginConfig

# Plugin configuration schema
class Config(PluginConfig):
    """Config schema for Test plugin"""
    enabled: bool = True

# Plugin class
class Plugin(PluginBase):
    slug = "test_plugin"
    name = "Test Plugin"
    description = "A simple test plugin to verify plugin loading works"
    version = "0.1.0"
    ConfigModel = Config
    
    def __init__(self, config: Config = None):
        super().__init__(config)
        self.router = APIRouter(prefix="/test-plugin", tags=["test-plugin"])
        
    def register_routes(self, app: FastAPI):
        # Register routes
        from .routes import router
        app.include_router(router, prefix="/api/v1")
        
        print("[test_plugin] Test plugin loaded successfully!")
        return True