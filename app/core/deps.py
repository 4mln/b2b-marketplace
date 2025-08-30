"""
Common Dependencies
Provides shared dependencies for plugins
"""
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db_sync
from app.core.db import get_session
from app.core.auth import get_current_user_sync, get_current_user_optional_sync
from plugins.auth.models import User

# Database dependencies
get_db = get_db_sync

# Authentication dependencies
get_current_user = get_current_user_sync
get_current_user_optional = get_current_user_optional_sync

# Type hints for better IDE support
__all__ = [
    "get_db",
    "get_current_user", 
    "get_current_user_optional",
    "Session",
    "AsyncSession",
    "User"
]
