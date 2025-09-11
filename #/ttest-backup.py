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

from app.core.db import Base
from app.db.session import get_session
from app.core.plugins.loader import PluginLoader

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
from plugins.ratings.models import *
from plugins.buyer.models import *
from plugins.payments.models import *
from plugins.seller.models import Seller

faker = Faker()

# --------------------------- Helpers ---------------------------

def fill_path_params(path: str) -> str:
    """Replace path parameters like {id} with dummy values."""
    return re.sub(r"\{.*?\}", "1", path)

def generate_dummy_payload(route: APIRoute) -> dict:
    """Generate minimal payload for POST/PUT routes based on endpoint signature."""
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
    """Fallback payload for known POST/PUT endpoints to avoid 422s."""
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
        "cart_data": {"items": []},
    }

# --------------------------- Test ---------------------------

@pytest.mark.asyncio
async def test_plugins_full_advanced_smoke():
    app = FastAPI()

    # ---------- SINGLE ENGINE & SESSIONMAKER ----------
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.execute(text("PRAGMA foreign_keys=ON"))
        await conn.run_sync(Base.metadata.create_all)

    # Seed minimal FK data
    async with async_session() as session:
        sellers_list = []

        # Users + Sellers
        for _ in range(3):
            user = User(
                username=faker.user_name(),
                email=faker.email(),
                hashed_password="hashedpass",
                is_active=True
            )
            session.add(user)
            await session.flush()

            seller = Seller(
                name=faker.company(),
                email=user.email,
                phone=faker.phone_number(),
                subscription="basic",
                user_id=user.id
            )
            session.add(seller)
            sellers_list.append(seller)
            await session.flush()

        # Guild
        guild = Guild(slug=faker.slug(), name="Test Guild", description="Demo guild")
        session.add(guild)
        await session.flush()

        # Products
        from plugins.products.models import Product
        for seller in sellers_list:
            product = Product(
                seller_id=seller.id,
                guild_id=guild.id,
                name=faker.word(),
                description="Simple product",
                price=10.0,
                stock=10,
                status="active"
            )
            session.add(product)

        # Cart
        from plugins.cart.models import Cart
        cart = Cart(user_id=sellers_list[0].user_id)
        session.add(cart)

        # Ads minimal FK
        ad_space = AdSpace(
            name="Main Banner",
            ad_type="banner",
            description="Main banner space",
            is_active=True
        )
        session.add(ad_space)
        await session.commit()
        
    # ---------- OVERRIDE SESSION FOR ROUTES ----------
    async def override_get_session() -> AsyncSession:
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    # Load plugins
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
    from httpx._transports.asgi import ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        for plugin_slug, plugin_routes in plugin_routes_map.items():
            for route in plugin_routes:
                path = fill_path_params(route.path)

                # Determine HTTP method, default to GET
                method = route.methods.pop() if route.methods else "GET"
                method = method.lower()

                # Generate payload for POST/PUT requests
                data = None
                if method in ("post", "put", "patch"):
                    data = generate_dummy_payload(route)

                # Send request
                response = await client.request(method, path, json=data)
                report.append((method.upper(), path, response.status_code))

    for method, path, status in report:
        print(f"{method} {path} -> {status}")

    # Assert all routes returned 200 or 404 (depending on accessibility)
    assert all(status in (200, 404) for _, _, status in report)
