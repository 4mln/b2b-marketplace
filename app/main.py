from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from app.core.config import settings
from app.core.db import engine  # make sure you export engine in db.py
from app.core.plugins import load_plugins
from app.core.connections import get_redis, get_rabbitmq_connection, redis_client, rabbitmq_connection
from app.api.routes.connections import router as connections_router

app = FastAPI(title="B2B Marketplace API")
app.include_router(connections_router)


@app.get("/")
async def root():
    return {"message": "API is running", "version": settings.APP_VERSION}


@app.on_event("startup")
async def startup_event():
    # Initialize Redis
    r = await get_redis()
    print("✅ Redis connected")

    # Initialize RabbitMQ
    rmq = await get_rabbitmq_connection()
    print("✅ RabbitMQ connected")

    # Initialize plugins (register routes + init DB)
    await load_plugins(app, engine)


@app.on_event("shutdown")
async def shutdown_event():
    # Close Redis
    if redis_client:
        await redis_client.close()
        print("🛑 Redis disconnected")

    # Close RabbitMQ
    if rabbitmq_connection:
        await rabbitmq_connection.close()
        print("🛑 RabbitMQ disconnected")