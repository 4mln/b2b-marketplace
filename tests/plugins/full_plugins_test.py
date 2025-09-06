# tests/plugins/test_all_plugins_full.py
import sys
import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.plugins.loader import PluginLoader
from app.core.db import engine

# Add project root to module path (if needed)
sys.path.append(os.path.abspath("."))

client = TestClient(app)

# ---------------------- Fixture to load plugins ----------------------
@pytest.fixture(scope="session")
async def loaded_plugins():
    """
    Async fixture to load all plugins once per test session.
    Returns a dict: slug -> plugin instance
    """
    loader = PluginLoader()

    # Import your async engine here
    from app.core.db import engine  # replace with your actual async engine

    plugins = await loader.load_all(app, engine)
    return {p.slug: p for p in plugins}

# ---------------------- Tests ----------------------
@pytest.mark.asyncio
async def test_plugins_loaded(loaded_plugins):
    """Ensure all plugins loaded successfully"""
    assert loaded_plugins, "No plugins were loaded"

@pytest.mark.asyncio
async def test_plugin_init_db(loaded_plugins):
    """Test that each plugin's init_db (if exists) works"""
    async_engine = engine
    for slug, plugin in loaded_plugins.items():
        if hasattr(plugin, "init_db"):
            try:
                await plugin.init_db(async_engine)  # make sure to await if it's async
            except Exception as e:
                pytest.fail(f"Plugin {slug} init_db failed: {e}")

@pytest.mark.asyncio
async def test_plugin_endpoints(loaded_plugins):
    """Test that plugin endpoints respond correctly"""
    for slug, plugin in loaded_plugins.items():
        if hasattr(plugin, "routes"):
            for route in plugin.routes:
                method = route.get("method", "GET").upper()
                path = route.get("path")
                if not path:
                    continue

                response = client.request(method, path)
                assert response.status_code < 500, (
                    f"Plugin {slug} endpoint {method} {path} failed with "
                    f"{response.status_code}"
                )

@pytest.mark.asyncio
async def test_plugin_crud_methods(loaded_plugins):
    """Test common CRUD methods minimally"""
    crud_methods = ["create", "list", "get", "update", "delete"]
    for slug, plugin in loaded_plugins.items():
        for method_name in crud_methods:
            method = getattr(plugin, method_name, None)
            if callable(method):
                try:
                    # Call method; skip if arguments required
                    result = method()
                except TypeError:
                    continue
                except Exception as e:
                    pytest.fail(f"Plugin {slug} method {method_name} failed: {e}")
