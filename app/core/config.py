from __future__ import annotations
from typing import Dict, Any
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # App metadata
    APP_NAME: str = "B2B Marketplace"
    APP_VERSION: str = "0.1.0"

    # Core services - use environment variables with fallbacks
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/marketplace"
    REDIS_URL: str = "redis://localhost:6379/0"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"

    # Security - use environment variable or generate a default
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Rate limiting
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    RATE_LIMIT_MAX_REQUESTS: int = 100

    # Plugin system
    ENABLE_PLUGIN_HOT_RELOAD: bool = False
    PLUGIN_CONFIG: Dict[str, Dict[str, Any]] = {}

    # Environment detection
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Override with environment variables if they exist
        if os.getenv("DATABASE_URL"):
            self.DATABASE_URL = os.getenv("DATABASE_URL")
        if os.getenv("REDIS_URL"):
            self.REDIS_URL = os.getenv("REDIS_URL")
        if os.getenv("RABBITMQ_URL"):
            self.RABBITMQ_URL = os.getenv("RABBITMQ_URL")
        if os.getenv("SECRET_KEY"):
            self.SECRET_KEY = os.getenv("SECRET_KEY")
        
        # Set environment-specific defaults
        if self.ENVIRONMENT == "production":
            self.DEBUG = False
            # In production, ensure we have proper secret key
            if self.SECRET_KEY == "your-secret-key-change-in-production":
                raise ValueError("SECRET_KEY must be set in production environment")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()