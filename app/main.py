# app/main.py
import asyncio
from app.core import rabbitmq
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from app.core.config import settings
from app.core.db import engine
from app.core.plugins import load_plugins
from app.core.connections import get_redis, get_rabbitmq_connection
from app.api.routes.connections import router as connections_router
from plugins.seller.routes import router as seller_router

app = FastAPI(title="B2B Marketplace API")
app.include_router(connections_router)
app.include_router(seller_router)

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

    # Initialize plugins (register routes + init DB)
    await load_plugins(app, engine)
    print("🔌 Plugins loaded")


@app.on_event("shutdown")
async def shutdown_event():
    # Close Redis
    try:
        await rabbitmq.stop_rabbit()
    except Exception:
        pass

    # Close RabbitMQ
    try:
        if hasattr(app.state, "rmq") and app.state.rmq:
            await app.state.rmq.close()
            print("🛑 RabbitMQ disconnected")
    except Exception:
        pass