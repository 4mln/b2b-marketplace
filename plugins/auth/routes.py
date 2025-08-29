# plugins/auth/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.core.db import get_session  # async DB session dependency
from plugins.user.security import get_current_user  # moved here for proper dependency
from app.core.openapi import enhance_endpoint_docs
from plugins.auth.docs import auth_docs
from pydantic import BaseModel
from datetime import datetime, timedelta
import random

router = APIRouter()

# -----------------------------
# Signup endpoint
# -----------------------------
@router.post("/signup", operation_id="signup")
async def signup(user_in=Depends(), db: AsyncSession = Depends(get_session)):
    # ✅ Local imports to avoid circular dependency
    from plugins.auth.schemas import UserCreate, UserOut
    from plugins.user.crud import create_user, get_user_by_email

    if not isinstance(user_in, UserCreate):
        user_in = UserCreate(**user_in.dict())

    existing_user = await get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_data = {
        "email": user_in.email,
        "full_name": user_in.full_name,
        "password": user_in.password,  # hashing handled in User CRUD
    }
    new_user = await create_user(db, user_data)
    return UserOut.model_validate(new_user)


# -----------------------------
# Login endpoint (OAuth2 standard)
# -----------------------------
@router.post("/token", operation_id="login_for_access_token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session),
):
    # ✅ Local imports
    from plugins.auth.schemas import Token
    from plugins.auth.jwt import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
    from plugins.user.crud import get_user_by_email
    from plugins.user.security import verify_password

    user = await get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


# -----------------------------
# Get current user
# -----------------------------
@router.get("/me", operation_id="read_current_user")
async def read_current_user(current_user=Depends(get_current_user)):
    # ✅ Local imports
    from plugins.auth.schemas import UserOut

    return UserOut.model_validate(current_user)


# -----------------------------
# OTP-first: request code to phone (Iran provider stub)
# -----------------------------
class OTPRequest(BaseModel):
    phone: str


@router.post("/otp/request", operation_id="otp_request")
async def otp_request(payload: OTPRequest, db: AsyncSession = Depends(get_session)):
    from plugins.auth.models import User
    from sqlalchemy import select
    # Find or create minimal user by phone
    result = await db.execute(select(User).where(User.phone == payload.phone))
    user = result.scalars().first()
    if not user:
        user = User(email=f"{payload.phone}@otp.local", phone=payload.phone, hashed_password="")
        db.add(user)
        await db.commit()
        await db.refresh(user)

    code = str(random.randint(100000, 999999))
    expiry = datetime.utcnow() + timedelta(minutes=10)
    user.otp_code = code
    user.otp_expiry = expiry
    await db.commit()

    # Send via Kavenegar (replace API key env var KAVENEGAR_API_KEY)
    try:
        import httpx, os
        api_key = os.getenv("KAVENEGAR_API_KEY")
        if api_key:
            url = f"https://api.kavenegar.com/v1/{api_key}/verify/lookup.json"
            params = {"receptor": payload.phone, "token": code, "template": "otp"}
            async with httpx.AsyncClient(timeout=10) as client:
                await client.get(url, params=params)
        else:
            print(f"[OTP:FALLBACK] {code} to {payload.phone}")
    except Exception as e:
        print(f"[OTP:ERROR] {e}")

    return {"detail": "OTP sent"}


# -----------------------------
# OTP-first: verify code and issue token
# -----------------------------
class OTPVerify(BaseModel):
    phone: str
    code: str


@router.post("/otp/verify", operation_id="otp_verify")
async def otp_verify(payload: OTPVerify, db: AsyncSession = Depends(get_session)):
    from plugins.auth.models import User
    from plugins.auth.jwt import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
    from sqlalchemy import select

    result = await db.execute(select(User).where(User.phone == payload.phone))
    user = result.scalars().first()
    if not user or not user.otp_code or not user.otp_expiry:
        raise HTTPException(status_code=400, detail="OTP not requested")
    if user.otp_code != payload.code or datetime.utcnow() > user.otp_expiry:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # clear otp and mark kyc tier1
    user.otp_code = None
    user.otp_expiry = None
    user.kyc_status = "otp_verified"
    await db.commit()

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Apply OpenAPI documentation enhancements
enhance_endpoint_docs(router, auth_docs)