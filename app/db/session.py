"""
Database Session Management
Provides both async and sync database session functions
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings

# Async session (from app/core/db.py)
from app.core.db import AsyncSessionLocal, get_session

# Sync engine and session for plugins that need sync operations
sync_engine = create_engine(
    settings.DATABASE_URL.replace("+asyncpg", ""),  # Remove asyncpg for sync
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
    """Synchronous database session dependency"""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Alias for backward compatibility
get_db = get_db_sync
