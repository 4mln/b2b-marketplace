# app/core/db.py
# Import all database components from app.db.session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.db.base import Base
from app.db.session import (
    async_engine,
    sync_engine,
    AsyncSessionLocal,
    SyncSessionLocal,
    get_session,
    get_db_sync,
    get_db_sync_dependency,
    get_db
)

# Re-export for backward compatibility
__all__ = [
    "Base", 
    "async_engine", 
    "engine",  # For backward compatibility
    "sync_engine", 
    "AsyncSessionLocal", 
    "SyncSessionLocal", 
    "get_session", 
    "get_db_sync",
    "get_db_sync_dependency",
    "get_db"
]

# Alias async_engine as engine for backward compatibility
engine = async_engine