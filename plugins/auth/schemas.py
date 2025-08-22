# plugins/auth/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional

# -----------------------------
# User input for signup
# -----------------------------
class UserCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    password: str

# -----------------------------
# User output (response)
# -----------------------------
class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool

    model_config = {
        "from_attributes": True
}
# -----------------------------
# JWT Token response
# -----------------------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# -----------------------------
# Token data inside JWT
# -----------------------------
class TokenData(BaseModel):
    username: Optional[str] = None