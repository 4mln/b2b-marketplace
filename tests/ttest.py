# tests/ttest.py
import pytest
import inspect
import re
from typing import List
from fastapi import FastAPI
from fastapi.routing import APIRoute
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from faker import Faker


# --------------------------- App & DB ---------------------------
from app.core.db import Base  # Make sure Base is the declarative_base
from app.db.session import get_session  # If you need it in plugins
from app.core.plugins.loader import PluginLoader

# Import all plugin models here so create_all sees them
from plugins.admin.models import *
from plugins.ads.models import *
from plugins.cart.models import *
from plugins.cms.models import *
from plugins.compliance.models import *
from plugins.escrow.models import *
from plugins.gamification.models import *
from plugins.guilds.models import *
from plugins.advanced_features.models import *
from plugins.user.models import *
from plugins.orders.models import *
from plugins.products.models import *
# ...repeat for all plugins with tables

faker = Faker()


# --------------------------- Helpers ---------------------------

def fill_path_params(path: str) -> str:
    """Replace path parameters like {id} with dummy values."""
    return re.sub(r"\{.*?\}", "1", path)


def generate_dummy_payload(route: APIRoute) -> dict:
    """Generate a minimal payload for POST/PUT routes based on endpoint signature."""
    payload = {}
    sig = inspect.signature(route.endpoint)
    for name, param in sig.parameters.items():
        if param.default is inspect.Parameter.empty:
            annotation = param.annotation
            if annotation in [int, float]:
                payload[name] = 1
            elif annotation == str:
                payload[name] = faker.word()
            elif annotation == bool:
                payload[name] = True
            else:
                payload[name] = faker.word()
    return payload


def generate_generic_payload():
    """Fallback payload for required fields we can't inspect."""
    return {
        "name": faker.word(),
        "email": faker.email(),
        "username": faker.user_name(),
        "product_id": 1,
        "quantity": 1,
        "ad_space_id": 1,
        "conversion_type": "click",
        "task": faker.word(),
        "prompt": faker.sentence(),
    }


# --------------------------- Test ---------------------------

@pytest.mark.asyncio
async def test_plugins_full_advanced_smoke():
    # Create FastAPI app and in-memory SQLite DB
    app = FastAPI()
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Create all tables and enable FK constraints
    async with engine.begin() as conn:
        await conn.execute(text("PRAGMA foreign_keys=ON"))
        await conn.run_sync(Base.metadata.create_all)

    # Insert minimal dummy FK data for users/products/etc.
    async with async_session() as session:
        # Example: create 5 users
        from plugins.user.models import User
        for _ in range(5):
            user = User(
                username=faker.user_name(),
                email=faker.email(),
                password="hashedpass"
            )
            session.add(user)
        # Example: create 5 products
        from plugins.products.models import Product
        for _ in range(5):
            product = Product(
                name=faker.word(),
                price=10.0
            )
            session.add(product)
        await session.commit()

    # Load all plugins
    loader = PluginLoader()
    plugins = await loader.load_all(app, engine)
    assert plugins, "No plugins loaded!"

    # Collect all routes
    routes: List[APIRoute] = [r for r in app.routes if isinstance(r, APIRoute)]
    assert routes, "No routes registered!"

    print(f"\n✅ Total plugins loaded: {len(plugins)}")
    print(f"✅ Total routes registered: {len(routes)}")

    # Map plugin -> routes
    plugin_routes_map = {}
    for plugin in plugins:
        plugin_routes_map[plugin.slug] = [
            r for r in routes if r.path.startswith(f"/{plugin.slug}") or plugin.slug in r.path
        ]

    # -------------------- Run route tests --------------------
    report = []
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        for plugin_slug, plugin_routes in plugin_routes_map.items():
            for route in plugin_routes:
                path = fill_path_params(route.path)
                methods = route.methods or ["GET"]

                for method in methods:
                    payload = None
                    if method in ["POST", "PUT"]:
                        payload = generate_dummy_payload(route) or generate_generic_payload()

                    try:
                        response = await client.request(method, path, json=payload)
                        status = response.status_code
                        info = response.text
                        if status in [401, 403]:
                            category = "AUTH_ERROR"
                        elif status >= 400:
                            category = "FAIL"
                        else:
                            category = "PASS"
                    except Exception as e:
                        status = "EXCEPTION"
                        info = str(e)
                        category = "FAIL"

                    report.append({
                        "plugin": plugin_slug,
                        "path": path,
                        "method": method,
                        "status": status,
                        "category": category,
                        "info": info
                    })

    # -------------------- Print structured report --------------------
    failed = [r for r in report if r["category"] != "PASS"]
    if failed:
        print("\n⚠️ Routes that failed (excluding auth warnings):")
        for r in failed:
            if r["category"] != "AUTH_ERROR":
                print(f"- [{r['category']}] {r['plugin']} | {r['method']} {r['path']} | "
                      f"Status/Error: {r['status']} | Info: {r['info'][:120]}...")
    else:
        print("\n✅ All plugin routes passed smoke test!")

    # -------------------- Assert --------------------
    assert not any(r for r in failed if r["category"] != "AUTH_ERROR"), \
        "Some plugin routes failed (excluding auth issues)!"
