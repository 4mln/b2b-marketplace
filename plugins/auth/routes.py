# plugins/auth/routes.py
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta, datetime
import random
import os
import shutil
from typing import List

from app.core.auth import get_current_user_sync as get_current_user
from app.core.openapi import enhance_endpoint_docs
from plugins.auth.docs import auth_docs
from plugins.auth.schemas import (
    UserCreate, UserOut, UserProfileOut, BusinessProfileUpdate, 
    KYCVerificationRequest, KYCVerificationResponse, UserProfileChangeOut,
    Token, OTPRequest, OTPVerify, PrivacySettings, NotificationPreferences,
    TwoFASetupOut, TwoFAToggle, TwoFAVerify
)
from plugins.auth.models import User, UserProfileChange
from plugins.auth.jwt import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from plugins.user.crud import create_user, get_user_by_email
from plugins.user.security import verify_password, get_password_hash
from sqlalchemy import select, update
from pydantic import BaseModel
import pyotp
from plugins.auth.models import UserSession

router = APIRouter()

# -----------------------------
# Signup endpoint
# -----------------------------
@router.post("/signup", operation_id="signup")
async def signup(user_in=Depends(), db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    if not isinstance(user_in, UserCreate):
        user_in = UserCreate(**user_in.dict())

    existing_user = await get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_data = {
        "email": user_in.email,
        "full_name": user_in.full_name,
        "phone": user_in.phone,
        "role": user_in.role,
        "password": user_in.password,
    }
    new_user = await create_user(db, user_data)
    return UserOut.model_validate(new_user)

# -----------------------------
# Login endpoint (OAuth2 standard)
# -----------------------------
@router.post("/token", operation_id="login_for_access_token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session),
):
    user = await get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Update last login
    await db.execute(update(User).where(User.id == user.id).values(last_login=datetime.utcnow()))
    await db.commit()

    # Create session record
    # Note: device info can be set via headers in a separate endpoint; minimal create here
    from plugins.auth.models import UserSession
    session = UserSession(user_id=user.id, user_agent="oauth2-password", ip_address=None)
    db.add(session)
    await db.commit()
    await db.refresh(session)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer", session_id=session.id)

# -----------------------------
# Get current user
# -----------------------------
@router.get("/me", operation_id="read_current_user")
async def read_current_user(current_user=Depends(get_current_user)):
    return UserOut.model_validate(current_user)

# -----------------------------
# Get complete user profile
# -----------------------------
@router.get("/me/profile", response_model=UserProfileOut, operation_id="read_user_profile")
async def read_user_profile(current_user=Depends(get_current_user), db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    return UserProfileOut.model_validate(current_user)

# -----------------------------
# Update user profile
# -----------------------------
@router.patch("/me/profile", response_model=UserProfileOut, operation_id="update_user_profile")
async def update_user_profile(
    profile_update: BusinessProfileUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session),
    request: Request = None
):
    # Calculate profile completion percentage
    completion_fields = [
        'business_name', 'business_type', 'business_industry', 'business_description',
        'business_phones', 'business_emails', 'website', 'business_addresses', 'bank_accounts'
    ]
    
    completed_fields = 0
    update_data = {}
    
    for field in completion_fields:
        if hasattr(profile_update, field) and getattr(profile_update, field) is not None:
            update_data[field] = getattr(profile_update, field)
            completed_fields += 1
    
    # Calculate completion percentage
    completion_percentage = min(100, int((completed_fields / len(completion_fields)) * 100))
    update_data['profile_completion_percentage'] = completion_percentage
    update_data['updated_at'] = datetime.utcnow()
    
    # Update user profile
    await db.execute(update(User).where(User.id == current_user.id).values(**update_data))
    await db.commit()
    await db.refresh(current_user)
    
    # Log profile change for audit trail
    if request:
        for field, value in update_data.items():
            if field != 'updated_at' and field != 'profile_completion_percentage':
                old_value = getattr(current_user, field, None)
                change = UserProfileChange(
                    user_id=current_user.id,
                    changed_by=current_user.id,
                    field_name=field,
                    old_value=str(old_value) if old_value is not None else None,
                    new_value=str(value) if value is not None else None,
                    change_type="update",
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent")
                )
                db.add(change)
        
        await db.commit()
    
    return UserProfileOut.model_validate(current_user)

# -----------------------------
# Upload business photo
# -----------------------------
@router.post("/me/profile/photo", operation_id="upload_business_photo")
async def upload_business_photo(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Create uploads directory if it doesn't exist
    upload_dir = "uploads/business_photos"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1]
    filename = f"business_photo_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update user profile
    await db.execute(
        update(User).where(User.id == current_user.id).values(business_photo=file_path)
    )
    await db.commit()
    
    return {"detail": "Business photo uploaded successfully", "file_path": file_path}

# -----------------------------
# Upload banner photo
# -----------------------------
@router.post("/me/profile/banner", operation_id="upload_banner_photo")
async def upload_banner_photo(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Create uploads directory if it doesn't exist
    upload_dir = "uploads/banner_photos"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1]
    filename = f"banner_photo_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update user profile
    await db.execute(
        update(User).where(User.id == current_user.id).values(banner_photo=file_path)
    )
    await db.commit()
    
    return {"detail": "Banner photo uploaded successfully", "file_path": file_path}

# -----------------------------
# KYC Verification
# -----------------------------
@router.post("/me/kyc/verify", response_model=KYCVerificationResponse, operation_id="kyc_verification")
async def kyc_verification(
    kyc_data: KYCVerificationRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    # Check if user has completed OTP verification
    if current_user.kyc_status == "pending":
        raise HTTPException(status_code=400, detail="Please complete OTP verification first")
    
    # Update user with KYC data
    update_data = {
        "business_name": kyc_data.business_name,
        "business_registration_number": kyc_data.business_registration_number,
        "business_tax_id": kyc_data.business_tax_id,
        "business_type": kyc_data.business_type,
        "business_industry": kyc_data.business_industry,
        "business_description": kyc_data.business_description,
        "business_phones": kyc_data.business_phones,
        "business_emails": kyc_data.business_emails,
        "business_addresses": [addr.dict() for addr in kyc_data.business_addresses],
        "bank_accounts": [acc.dict() for acc in kyc_data.bank_accounts],
        "kyc_status": "business_verified",
        "kyc_verified_at": datetime.utcnow(),
        "profile_completion_percentage": 100,
        "updated_at": datetime.utcnow()
    }
    
    await db.execute(update(User).where(User.id == current_user.id).values(**update_data))
    await db.commit()
    
    return KYCVerificationResponse(
        status="business_verified",
        message="KYC verification submitted successfully. Your profile will be reviewed within 24-48 hours.",
        estimated_processing_time="24-48 hours"
    )

# -----------------------------
# Get profile change history
# -----------------------------
@router.get("/me/profile/changes", response_model=List[UserProfileChangeOut], operation_id="get_profile_changes")
async def get_profile_changes(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session),
    limit: int = 50
):
    result = await db.execute(
        select(UserProfileChange)
        .where(UserProfileChange.user_id == current_user.id)
        .order_by(UserProfileChange.created_at.desc())
        .limit(limit)
    )
    changes = result.scalars().all()
    return [UserProfileChangeOut.model_validate(change) for change in changes]

# -----------------------------
# Update privacy settings
# -----------------------------
@router.patch("/me/privacy", operation_id="update_privacy_settings")
async def update_privacy_settings(
    privacy_settings: PrivacySettings,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    await db.execute(
        update(User).where(User.id == current_user.id).values(
            privacy_settings=privacy_settings.dict(),
            updated_at=datetime.utcnow()
        )
    )
    await db.commit()
    
    return {"detail": "Privacy settings updated successfully"}

# -----------------------------
# Update notification preferences
# -----------------------------
@router.patch("/me/notifications", operation_id="update_notification_preferences")
async def update_notification_preferences(
    notification_preferences: NotificationPreferences,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)
):
    await db.execute(
        update(User).where(User.id == current_user.id).values(
            notification_preferences=notification_preferences.dict(),
            updated_at=datetime.utcnow()
        )
    )
    await db.commit()
    
    return {"detail": "Notification preferences updated successfully"}

# -----------------------------
# OTP-first: request code to phone (Iran provider stub)
# -----------------------------
@router.post("/otp/request", operation_id="otp_request")
async def otp_request(payload: OTPRequest, db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
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
@router.post("/otp/verify", operation_id="otp_verify")
async def otp_verify(payload: OTPVerify, db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
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
    user.last_login = datetime.utcnow()
    await db.commit()

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}

# -----------------------------
# 2FA (TOTP)
# -----------------------------
@router.post("/me/2fa/setup", response_model=TwoFASetupOut)
async def setup_2fa(current_user=Depends(get_current_user), db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    if current_user.two_factor_enabled and current_user.totp_secret:
        # Return existing provisioning URI
        totp = pyotp.TOTP(current_user.totp_secret)
        uri = totp.provisioning_uri(name=current_user.email, issuer_name="B2B-Marketplace")
        return TwoFASetupOut(provisioning_uri=uri, secret=current_user.totp_secret)

    secret = pyotp.random_base32()
    await db.execute(update(User).where(User.id == current_user.id).values(totp_secret=secret, updated_at=datetime.utcnow()))
    await db.commit()
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=current_user.email, issuer_name="B2B-Marketplace")
    return TwoFASetupOut(provisioning_uri=uri, secret=secret)

@router.post("/me/2fa/verify")
async def verify_2fa(payload: TwoFAVerify, current_user=Depends(get_current_user), db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    if not current_user.totp_secret:
        raise HTTPException(status_code=400, detail="2FA not initialized")
    totp = pyotp.TOTP(current_user.totp_secret)
    if not totp.verify(payload.code, valid_window=1):
        raise HTTPException(status_code=400, detail="Invalid code")
    await db.execute(update(User).where(User.id == current_user.id).values(two_factor_enabled=True, updated_at=datetime.utcnow()))
    await db.commit()
    return {"detail": "2FA enabled"}

@router.post("/me/2fa/toggle")
async def toggle_2fa(payload: TwoFAToggle, current_user=Depends(get_current_user), db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    if payload.enabled and not current_user.totp_secret:
        raise HTTPException(status_code=400, detail="Setup 2FA first")
    await db.execute(update(User).where(User.id == current_user.id).values(two_factor_enabled=payload.enabled, updated_at=datetime.utcnow()))
    await db.commit()
    return {"detail": f"2FA {'enabled' if payload.enabled else 'disabled'}"}

# -----------------------------
# Sessions management
# -----------------------------
@router.get("/me/sessions", response_model=list[dict])
async def list_sessions(current_user=Depends(get_current_user), db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    result = await db.execute(select(UserSession).where(UserSession.user_id == current_user.id).order_by(UserSession.created_at.desc()))
    sessions = result.scalars().all()
    return [
        {
            "id": s.id,
            "device_id": s.device_id,
            "user_agent": s.user_agent,
            "ip_address": s.ip_address,
            "created_at": s.created_at,
            "last_seen_at": s.last_seen_at,
            "is_revoked": s.is_revoked,
        }
        for s in sessions
    ]

@router.post("/me/sessions/{session_id}/revoke")
async def revoke_session(session_id: int, current_user=Depends(get_current_user), db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    s = await db.get(UserSession, session_id)
    if not s or s.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    s.is_revoked = True
    s.last_seen_at = datetime.utcnow()
    await db.commit()
    return {"detail": "Session revoked"}

@router.post("/me/sessions/logout-all")
async def logout_all_sessions(current_user=Depends(get_current_user), db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    result = await db.execute(select(UserSession).where(UserSession.user_id == current_user.id))
    sessions = result.scalars().all()
    for s in sessions:
        s.is_revoked = True
        s.last_seen_at = datetime.utcnow()
    await db.commit()
    return {"detail": "All sessions revoked"}

# Apply OpenAPI documentation enhancements
enhance_endpoint_docs(router, auth_docs)