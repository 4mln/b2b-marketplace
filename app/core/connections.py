# app/core/connections.py
import redis.asyncio as redis_async
import aio_pika
from app.core.config import settings

# Redis connection
redis_client: redis_async.Redis | None = None

async def get_redis() -> redis_async.Redis:
    global redis_client
    if not redis_client:
        redis_client = redis_async.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        await redis_client.ping()
    return redis_client

# RabbitMQ connection
rabbitmq_connection: aio_pika.RobustConnection | None = None

async def get_rabbitmq_connection() -> aio_pika.RobustConnection:
    global rabbitmq_connection
    if not rabbitmq_connection:
        rabbitmq_connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    return rabbitmq_connection