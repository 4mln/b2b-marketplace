# app/main.py
import asyncio
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from app.core import rabbitmq
from app.core.config import settings
from app.core.db import engine
from app.core.plugins import load_plugins
from app.core.connections import get_redis

# Only include connection routes manually
from app.api.routes.connections import router as connections_router

app = FastAPI(title="B2B Marketplace API")
app.include_router(connections_router)

@app.get("/")
async def root():
    return {"message": "API is running", "version": settings.APP_VERSION}


@app.on_event("startup")
async def startup_event():
    # Initialize Redis
    try:
        app.state.redis = await get_redis()
        print("✅ Redis connected")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")

    # Initialize RabbitMQ
    try:
        app.state.rmq_conn, _ = await rabbitmq.get_connection()
        await rabbitmq.start_consumer()
        print("✅ RabbitMQ connected and consumer started")
    except Exception as e:
        print(f"❌ RabbitMQ connection failed: {e}")

    # Load all plugins (routes + DB)
    loaded_plugins = await load_plugins(app, engine)
    print("🔌 Plugins loaded:", [p.__class__.__name__ for p in loaded_plugins])

    # Optional: Print all registered routes
    print("📌 Registered routes:")
    for route in app.routes:
        print(f"  {route.path} -> {route.name}")


@app.on_event("shutdown")
async def shutdown_event():
    # Close Redis
    if hasattr(app.state, "redis") and app.state.redis:
        try:
            await app.state.redis.close()
            print("🛑 Redis disconnected")
        except Exception:
            pass

    # Close RabbitMQ
    if hasattr(app.state, "rmq_conn") and app.state.rmq_conn:
        try:
            await app.state.rmq_conn.close()
            print("🛑 RabbitMQ disconnected")
        except Exception:
            pass