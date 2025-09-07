# tests/plugins/full_plugins_test.py
import pytest
import asyncio
from httpx import AsyncClient
from faker import Faker
from app.main import app
from app.core.plugins.loader import PluginLoader
from app.core.db import engine
import pytest_asyncio

faker = Faker()

# ---------------------- ANSI color codes ----------------------
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def log_pass(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def log_fail(msg):
    print(f"{RED}❌ {msg}{RESET}")

def log_skip(msg):
    print(f"{YELLOW}⚠️ {msg}{RESET}")

# ---------------------- Result collector ----------------------
plugin_results = {}  # slug -> {"pass": int, "fail": int, "skip": int, "details": list}

def add_result(slug, status, detail=None):
    if slug not in plugin_results:
        plugin_results[slug] = {"pass": 0, "fail": 0, "skip": 0, "details": []}
    plugin_results[slug][status] += 1
    if detail:
        plugin_results[slug]["details"].append(detail)

# ---------------------- Fixtures ----------------------
@pytest_asyncio.fixture(scope="session")
async def loaded_plugins():
    loader = PluginLoader()
    plugins = await loader.load_all(app, engine)
    log_pass(f"Loaded {len(plugins)} plugins")
    return {p.slug: p for p in plugins}  # Already a dict

@pytest_asyncio.fixture(scope="session")
async def async_client():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client

# ---------------------- Plugin tests ----------------------
@pytest.mark.asyncio
async def test_plugins_loaded(loaded_plugins):
    assert loaded_plugins, log_fail("No plugins were loaded")
    for slug in loaded_plugins.keys():
        add_result(slug, "pass")
    log_pass(f"Plugins loaded: {list(loaded_plugins.keys())}")

@pytest.mark.asyncio
async def test_plugin_init_db(loaded_plugins, test_engine):
    for slug, plugin in loaded_plugins.items():
        if hasattr(plugin, "init_db"):
            try:
                await plugin.init_db(test_engine)
                print(f"✅ Plugin '{slug}' init_db executed")
            except Exception as e:
                pytest.fail(f"Plugin '{slug}' init_db failed: {e}")

@pytest.mark.asyncio
async def test_plugin_endpoints(loaded_plugins, async_client):
    for slug, plugin in loaded_plugins.items():
        if hasattr(plugin, "routes"):
            for route in plugin.routes:
                path = route.get("path")
                method = route.get("method", "GET").upper()
                if not path:
                    add_result(slug, "skip", "route has no path")
                    log_skip(f"Plugin '{slug}' has route with no path")
                    continue

                payload = None
                if method in ["POST", "PUT"]:
                    payload = {
                        "name": faker.word(),
                        "description": faker.sentence(),
                        "price": round(faker.random_number(digits=3), 2)
                    }

                try:
                    response = await async_client.request(method, path, json=payload)
                    if response.status_code < 500:
                        add_result(slug, "pass", f"{method} {path} -> {response.status_code}")
                        log_pass(f"Plugin '{slug}' endpoint {method} {path} returned {response.status_code}")
                    else:
                        add_result(slug, "fail", f"{method} {path} -> {response.status_code}")
                        log_fail(f"Plugin '{slug}' endpoint {method} {path} failed with {response.status_code}")
                except Exception as e:
                    add_result(slug, "fail", f"{method} {path} error: {e}")
                    log_fail(f"Plugin '{slug}' endpoint {method} {path} error: {e}")
                    pytest.fail(f"Plugin '{slug}' endpoint {method} {path} error: {e}")

@pytest.mark.asyncio
async def test_plugin_crud_methods(loaded_plugins):
    crud_methods = ["create", "list", "get", "update", "delete"]

    for slug, plugin in loaded_plugins.items():
        created_items = []

        for method_name in crud_methods:
            method = getattr(plugin, method_name, None)
            if callable(method):
                try:
                    # CREATE
                    if method_name == "create":
                        fake_data = {
                            "name": faker.word(),
                            "description": faker.sentence(),
                            "price": round(faker.random_number(digits=3), 2)
                        }
                        result = await method(**fake_data) if asyncio.iscoroutinefunction(method) else method(**fake_data)
                        add_result(slug, "pass", "create executed")
                        log_pass(f"Plugin '{slug}' method 'create' executed")
                        if hasattr(result, "id"):
                            created_items.append(result.id)

                    # UPDATE
                    elif method_name == "update":
                        if not created_items:
                            add_result(slug, "skip", "update skipped (no items)")
                            log_skip(f"Plugin '{slug}' method 'update' skipped (no items)")
                            continue
                        await method(created_items[0]) if asyncio.iscoroutinefunction(method) else method(created_items[0])
                        add_result(slug, "pass", "update executed")
                        log_pass(f"Plugin '{slug}' method 'update' executed")

                    # DELETE
                    elif method_name == "delete":
                        if not created_items:
                            add_result(slug, "skip", "delete skipped (no items)")
                            log_skip(f"Plugin '{slug}' method 'delete' skipped (no items)")
                            continue
                        await method(created_items.pop()) if asyncio.iscoroutinefunction(method) else method(created_items.pop())
                        add_result(slug, "pass", "delete executed")
                        log_pass(f"Plugin '{slug}' method 'delete' executed")

                    # GET
                    elif method_name == "get":
                        if not created_items:
                            add_result(slug, "skip", "get skipped (no items)")
                            log_skip(f"Plugin '{slug}' method 'get' skipped (no items)")
                            continue
                        await method(created_items[0]) if asyncio.iscoroutinefunction(method) else method(created_items[0])
                        add_result(slug, "pass", "get executed")
                        log_pass(f"Plugin '{slug}' method 'get' executed")

                    # LIST or others
                    else:
                        await method() if asyncio.iscoroutinefunction(method) else method()
                        add_result(slug, "pass", f"{method_name} executed")
                        log_pass(f"Plugin '{slug}' method '{method_name}' executed")

                except TypeError:
                    add_result(slug, "skip", f"{method_name} skipped (args mismatch)")
                    log_skip(f"Plugin '{slug}' method '{method_name}' skipped (args mismatch)")
                    continue
                except Exception as e:
                    add_result(slug, "fail", f"{method_name} failed: {e}")
                    log_fail(f"Plugin '{slug}' method '{method_name}' failed: {e}")
                    pytest.fail(f"Plugin '{slug}' method '{method_name}' failed: {e}")

        # Cleanup
        delete_method = getattr(plugin, "delete", None)
        if callable(delete_method):
            for item_id in created_items:
                try:
                    await delete_method(item_id) if asyncio.iscoroutinefunction(delete_method) else delete_method(item_id)
                except Exception:
                    pass

# ---------------------- Summary at the end ----------------------
def pytest_sessionfinish(session, exitstatus):
    print("\n\n========== Plugins Test Summary ==========")
    for slug, info in plugin_results.items():
        print(f"\nPlugin: {slug}")
        print(f"PASS: {info['pass']}  FAIL: {info['fail']}  SKIP: {info['skip']}")
        if info["details"]:
            print("Details:")
            for detail in info["details"]:
                print(f"  - {detail}")
    print("=" * 50)
