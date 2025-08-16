# app/core/connections.py
import asyncio
import logging
import redis.asyncio as redis_async
import aio_pika
from app.core.config import settings

logger = logging.getLogger(__name__)

# Redis singleton
_redis_instance: redis_async.Redis | None = None

async def get_redis(max_retries: int = 5, delay: float = 2.0) -> redis_async.Redis:
    """Return a connected Redis instance with retry logic."""
    global _redis_instance
    if _redis_instance:
        return _redis_instance

    for attempt in range(1, max_retries + 1):
        try:
            _redis_instance = redis_async.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            await _redis_instance.ping()
            logger.info("✅ Redis connected")
            return _redis_instance
        except Exception as e:
            logger.warning(f"Redis connection attempt {attempt} failed: {e}")
            await asyncio.sleep(delay)

    raise ConnectionError(f"Failed to connect to Redis at {settings.REDIS_URL} after {max_retries} attempts")


# RabbitMQ singleton
_rabbitmq_instance: aio_pika.RobustConnection | None = None

async def get_rabbitmq_connection(max_retries: int = 5, delay: float = 2.0) -> aio_pika.RobustConnection:
    """Return a connected RabbitMQ instance with retry logic."""
    global _rabbitmq_instance
    if _rabbitmq_instance:
        return _rabbitmq_instance

    for attempt in range(1, max_retries + 1):
        try:
            _rabbitmq_instance = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            logger.info("✅ RabbitMQ connected")
            return _rabbitmq_instance
        except Exception as e:
            logger.warning(f"RabbitMQ connection attempt {attempt} failed: {e}")
            await asyncio.sleep(delay)

    raise ConnectionError(f"Failed to connect to RabbitMQ at {settings.RABBITMQ_URL} after {max_retries} attempts")