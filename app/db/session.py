"""Database Session Management
Provides both async and sync database session functions
"""
from sqlalchemy.ext.asyncio import AsyncSession , create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings

# Create our own async session to avoid circular imports
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.db.base import Base

# Async engine
async_engine = create_async_engine(
    settings.DATABASE_URL,
    future=True,
    echo=False
)

# Async session factory
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency to use in FastAPI routes
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# Sync engine and session for plugins that need sync operations
sync_engine = create_engine(
    settings.DATABASE_URL.replace("+asyncpg", "+psycopg2"),  # Replace asyncpg with psycopg2 for sync
    echo=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    class_=Session,
    expire_on_commit=False
)

def get_db_sync() -> Session:
    """Synchronous database session dependency for FastAPI"""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Alias for backward compatibility
get_db_sync_dependency = get_db_sync
get_db = get_db_sync


