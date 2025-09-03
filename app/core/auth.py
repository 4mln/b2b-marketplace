"""
Core Authentication Module
Provides centralized authentication functions for the B2B marketplace
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import Optional
import jwt
from datetime import datetime, timedelta

from app.core.config import settings
from plugins.auth.models import User
from plugins.auth.jwt import verify_token

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_session)
) -> User:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(token, credentials_exception)
        user_id: str = payload.get("sub")
        if not user_id:
            raise credentials_exception
        
        # Get user from database
        result = await db.execute(
            "SELECT * FROM users WHERE id = :user_id AND is_active = true",
            {"user_id": int(user_id)}
        )
        user_data = result.fetchone()
        
        if not user_data:
            raise credentials_exception
        
        # Convert to User object
        user = User(
            id=user_data.id,
            email=user_data.email,
            full_name=user_data.full_name,
            is_active=user_data.is_active,
            role=user_data.role
        )
        
        return user
    except Exception as e:
        raise credentials_exception

async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_session)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    if not token:
        return None
    
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None

def get_current_user_sync(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db_sync)
) -> User:
    """Synchronous version of get_current_user for sync routes"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(token, credentials_exception)
        user_id: str = payload.get("sub")
        if not user_id:
            raise credentials_exception
        
        # Get user from database
        user = db.query(User).filter(
            User.id == int(user_id),
            User.is_active == True
        ).first()
        
        if not user:
            raise credentials_exception
        
        return user
    except Exception as e:
        raise credentials_exception

def get_current_user_optional_sync(
    token: Optional[str] = Depends(oauth2_scheme), 
    db: Session = Depends(get_db_sync)
) -> Optional[User]:
    """Synchronous version of get_current_user_optional"""
    if not token:
        return None
    
    try:
        return get_current_user_sync(token, db)
    except HTTPException:
        return None

# Import database session functions directly to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import Session


