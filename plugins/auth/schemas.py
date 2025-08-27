# plugins/auth/schemas.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime

# -----------------------------
# User Schemas
# -----------------------------
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    model_config = ConfigDict(extra="forbid")

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    model_config = ConfigDict(extra="forbid")

class UserOut(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# -----------------------------
# Token Schemas
# -----------------------------
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token expiration time in seconds")

class TokenPayload(BaseModel):
    sub: str
    exp: datetime
    refresh: Optional[bool] = False

class RefreshTokenRequest(BaseModel):
    refresh_token: str
    model_config = ConfigDict(extra="forbid")