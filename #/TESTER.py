# tests/full_ultimate_backend_test.py
import pytest
import pytest_asyncio
import asyncio
import inspect
import re
from typing import List, Dict, Any
from fastapi.routing import APIRoute
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.inspection import inspect as sa_inspect
from faker import Faker
from enum import Enum

from app.main import app as main_app
from app.core.db import Base
from app.core.plugins.loader import PluginLoader
import plugins  # Ensure every plugin's models are imported in plugin __init__ or dynamically

import warnings
# -------------------- Suppress known deprecation warnings --------------------
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pytest_asyncio")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="passlib")

faker = Faker()

# ---------------------- ANSI color codes ----------------------
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def log_pass(msg): print(f"{GREEN}✅ {msg}{RESET}")
def log_fail(msg): print(f"{RED}❌ {msg}{RESET}")
def log_skip(msg): print(f"{YELLOW}⚠️ {msg}{RESET}")

plugin_results = {}
def add_result(slug, status, detail=None):
    if slug not in plugin_results:
        plugin_results[slug] = {"pass":0,"fail":0,"skip":0,"details":[]}
    plugin_results[slug][status] += 1
    if detail:
        plugin_results[slug]["details"].append(detail)

# ---------------------- Helper Functions ----------------------
def fill_path_params(path: str) -> str:
    return re.sub(r"\{.*?\}", "1", path)

def generate_value(annotation):
    if annotation in [int, float]: return 1
    elif annotation == str: return faker.word()
    elif annotation == bool: return True
    elif inspect.isclass(annotation) and issubclass(annotation, Enum): return list(annotation)[0]
    elif inspect.isclass(annotation) and issubclass(annotation, dict): return {}
    elif inspect.isclass(annotation) and issubclass(annotation, list): return []
    else: return faker.word()

def generate_dummy_payload_recursive(func, fk_records: Dict[str, List[int]]):
    payload = {}
    sig = inspect.signature(func)
    for name, param in sig.parameters.items():
        if param.default is inspect.Parameter.empty:
            ann = param.annotation
            fk_table = getattr(ann, "__tablename__", None)
            if fk_table and fk_table in fk_records and fk_records[fk_table]:
                payload[name] = fk_records[fk_table][0]
            else:
                payload[name] = generate_value(ann)
    return payload

async def retry_async(func, *args, retries=3, delay=0.5, **kwargs):
    last_exception = None
    for _ in range(retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            await asyncio.sleep(delay)
    raise last_exception

def get_all_models():
    models = []
    for mapper in Base.registry.mappers:
        cls = mapper.class_
        if isinstance(cls, type) and issubclass(cls, Base):
            models.append(cls)
    return models

async def auto_seed_fk(session: AsyncSession):
    models = get_all_models()
    fk_records = {}
    for model in models:
        # Example: check for FKs
        cols = [col for col in sa_inspect(model).columns if col.foreign_keys]
        if cols:
            print(f"Found FK in {model.__name__}: {[c.name for c in cols]}")
            for col in cols:
                fk_records[col.table.name] = [1]  # dummy FK id
            # Here you can insert dummy seed records if needed
    return fk_records

# ---------------------- Dependency Sorting ----------------------
def topological_sort_plugins(plugins_dict: Dict[str, Any]):
    sorted_list = []
    visited = set()
    temp_mark = set()
    def visit(slug):
        if slug in visited: return
        if slug in temp_mark: raise Exception(f"Circular dependency at plugin: {slug}")
        temp_mark.add(slug)
        plugin = plugins_dict[slug]
        deps = getattr(plugin, "dependencies", [])
        for dep in deps:
            if dep not in plugins_dict: raise Exception(f"Dependency '{dep}' of '{slug}' not found")
            visit(dep)
        temp_mark.remove(slug)
        visited.add(slug)
        sorted_list.append(slug)
    for slug in plugins_dict.keys(): visit(slug)
    return [plugins_dict[slug] for slug in sorted_list]

# ---------------------- Fixtures ----------------------
@pytest_asyncio.fixture(scope="session")
async def test_engine():
    DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/b2b_test_db"
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    return engine

@pytest_asyncio.fixture(scope="session")
async def async_session(test_engine):
    return sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture(scope="session")
async def loaded_plugins(test_engine):
    loader = PluginLoader()
    plugins_dict = {p.slug: p for p in await loader.load_all(main_app, test_engine)}
    print(f"✅ Loaded {len(plugins_dict)} plugins")
    sorted_plugins = topological_sort_plugins(plugins_dict)
    return {p.slug: p for p in sorted_plugins}

@pytest_asyncio.fixture(scope="session")
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=main_app), base_url="http://testserver") as client:
        yield client

# ---------------------- Dependency-Aware CRUD & Endpoint Test ----------------------
@pytest.mark.asyncio
async def test_plugin_crud_and_endpoints(loaded_plugins, async_session, async_client):
    async with async_session() as session:
        fk_records = await auto_seed_fk(session)
        for slug, plugin in loaded_plugins.items():
            print(f"\n--- Testing plugin: {slug} ---")
            created_items = []

            # CRUD
            for method_name in ["create","list","get","update","delete"]:
                method = getattr(plugin, method_name, None)
                if callable(method):
                    payload = generate_dummy_payload_recursive(method, fk_records)
                    try:
                        if method_name == "create":
                            result = await retry_async(method, **payload) if asyncio.iscoroutinefunction(method) else method(**payload)
                            add_result(slug,"pass","create executed")
                            pk = getattr(result,"id",None)
                            if pk: created_items.append(pk)
                        elif method_name == "update":
                            if not created_items: add_result(slug,"skip","update skipped"); continue
                            await retry_async(method, created_items[0], **payload) if asyncio.iscoroutinefunction(method) else method(created_items[0], **payload)
                            add_result(slug,"pass","update executed")
                        elif method_name == "delete":
                            if not created_items: add_result(slug,"skip","delete skipped"); continue
                            await retry_async(method, created_items.pop()) if asyncio.iscoroutinefunction(method) else method(created_items.pop())
                            add_result(slug,"pass","delete executed")
                        elif method_name == "get":
                            if not created_items: add_result(slug,"skip","get skipped"); continue
                            await retry_async(method, created_items[0]) if asyncio.iscoroutinefunction(method) else method(created_items[0])
                            add_result(slug,"pass","get executed")
                        else:
                            await retry_async(method) if asyncio.iscoroutinefunction(method) else method()
                            add_result(slug,"pass",f"{method_name} executed")
                    except Exception as e:
                        add_result(slug,"fail",f"{method_name} failed: {e}")

            # Endpoints
            routes = [
                r for r in main_app.routes  
                if isinstance(r, APIRoute) and (r.path.startswith(f"/{slug}") or slug in r.path)
            ]
            for route in routes:
                path = fill_path_params(route.path)
                method = next(iter(route.methods)) if route.methods else "GET"
                method = method.lower()
                data = None
                if method in ("post","put","patch"): data = generate_dummy_payload_recursive(route.endpoint,fk_records)
                try:
                    response = await retry_async(async_client.request, method, path, json=data)
                    status = response.status_code
                    if status < 500: add_result(slug,"pass",f"{method.upper()} {path} -> {status}")
                    else: add_result(slug,"fail",f"{method.upper()} {path} -> {status}")
                except Exception as e:
                    add_result(slug,"fail",f"{method.upper()} {path} error: {e}")

# ---------------------- Final Summary ----------------------
def pytest_sessionfinish(session, exitstatus):
    print("\n\n========== Plugins Test Summary ==========")
    for slug, info in plugin_results.items():
        print(f"\nPlugin: {slug}")
        print(f"PASS: {info['pass']}  FAIL: {info['fail']}  SKIP: {info['skip']}")
        if info["details"]:
            print("Details:")
            for detail in info["details"]:
                print(f"  - {detail}")
    print("="*50)