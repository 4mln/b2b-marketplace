import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "B2B Marketplace"
    APP_VERSION: str = "0.1.0"

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://postgres:postgres@db:5432/marketplace"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")

    class Config:
        env_file = ".env"

settings = Settings()