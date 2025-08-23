from __future__ import annotations
from typing import Dict, Any
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App metadata
    APP_NAME: str = "B2B Marketplace"
    APP_VERSION: str = "0.1.0"

    # Core services (match existing usage in db/connections)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/b2b_marketplace"
    REDIS_URL: str = "redis://redis:6379/0"
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"

    # Plugin system
    ENABLE_PLUGIN_HOT_RELOAD: bool = False
    PLUGIN_CONFIG: Dict[str, Dict[str, Any]] = {}

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()