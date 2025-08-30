# plugins/auth/schemas.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# -----------------------------
# Enums
# -----------------------------
class BusinessType(str, Enum):
    INDIVIDUAL = "individual"
    COMPANY = "company"
    PARTNERSHIP = "partnership"

class KYCStatus(str, Enum):
    PENDING = "pending"
    OTP_VERIFIED = "otp_verified"
    BUSINESS_VERIFIED = "business_verified"
    REJECTED = "rejected"

class UserRole(str, Enum):
    USER = "user"
    SELLER = "seller"
    BUYER = "buyer"
    BOTH = "both"

# -----------------------------
# OTP Schemas
# -----------------------------
class OTPRequest(BaseModel):
    phone: str = Field(..., description="Phone number for OTP verification")

class OTPVerify(BaseModel):
    phone: str = Field(..., description="Phone number")
    code: str = Field(..., description="OTP verification code")

# -----------------------------
# Business Information Schemas
# -----------------------------
class BusinessAddress(BaseModel):
    title: str = Field(..., description="Address title (e.g., 'Main Office', 'Warehouse')")
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: Optional[str] = None
    postal_code: str
    country: str = "Iran"
    is_primary: bool = False

class BankAccount(BaseModel):
    bank_name: str
    account_number: str
    account_holder: str
    iban: Optional[str] = None
    is_primary: bool = False

class PrivacySettings(BaseModel):
    profile_visibility: str = "public"  # public, private, guild_only
    contact_info_visibility: str = "public"  # public, private, verified_only
    business_info_visibility: str = "public"  # public, private, verified_only
    allow_messages: bool = True
    allow_quotes: bool = True

class NotificationPreferences(BaseModel):
    email_notifications: bool = True
    sms_notifications: bool = True
    push_notifications: bool = True
    telegram_notifications: bool = False
    whatsapp_notifications: bool = False
    marketing_emails: bool = False
    order_updates: bool = True
    quote_notifications: bool = True
    price_alerts: bool = False

# -----------------------------
# User Schemas
# -----------------------------
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    phone: Optional[str] = None
    role: UserRole = UserRole.USER
    model_config = ConfigDict(extra="forbid")

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    model_config = ConfigDict(extra="forbid")

class BusinessProfileUpdate(BaseModel):
    # Business Information
    business_name: Optional[str] = None
    business_registration_number: Optional[str] = None
    business_tax_id: Optional[str] = None
    business_type: Optional[BusinessType] = None
    business_industry: Optional[str] = None
    business_description: Optional[str] = None
    
    # Contact Details
    business_phones: Optional[List[str]] = Field(None, max_items=4)
    business_emails: Optional[List[str]] = Field(None, max_items=5)
    website: Optional[str] = None
    telegram_id: Optional[str] = None
    whatsapp_id: Optional[str] = None
    
    # Addresses and Bank Accounts
    business_addresses: Optional[List[BusinessAddress]] = Field(None, max_items=3)
    bank_accounts: Optional[List[BankAccount]] = Field(None, max_items=3)
    
    # Privacy and Preferences
    privacy_settings: Optional[PrivacySettings] = None
    notification_preferences: Optional[NotificationPreferences] = None
    
    model_config = ConfigDict(extra="forbid")
    
    @validator('business_phones')
    def validate_phone_numbers(cls, v):
        if v is not None:
            for phone in v:
                if not phone or len(phone) < 10:
                    raise ValueError("Invalid phone number")
        return v
    
    @validator('business_emails')
    def validate_emails(cls, v):
        if v is not None:
            for email in v:
                if not email or '@' not in email:
                    raise ValueError("Invalid email address")
        return v

class UserOut(UserBase):
    id: int
    phone: Optional[str] = None
    role: UserRole
    is_active: bool
    is_superuser: bool
    kyc_status: KYCStatus
    profile_completion_percentage: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    # Business Information (only if user has completed profile)
    business_name: Optional[str] = None
    business_type: Optional[BusinessType] = None
    business_industry: Optional[str] = None
    website: Optional[str] = None
    telegram_id: Optional[str] = None
    whatsapp_id: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class UserProfileOut(UserOut):
    """Complete user profile with all business information"""
    # Full Business Information
    business_registration_number: Optional[str] = None
    business_tax_id: Optional[str] = None
    business_description: Optional[str] = None
    business_phones: Optional[List[str]] = None
    business_emails: Optional[List[str]] = None
    business_addresses: Optional[List[BusinessAddress]] = None
    bank_accounts: Optional[List[BankAccount]] = None
    business_photo: Optional[str] = None
    banner_photo: Optional[str] = None
    
    # Privacy and Preferences
    privacy_settings: Optional[PrivacySettings] = None
    notification_preferences: Optional[NotificationPreferences] = None
    
    # KYC Information
    kyc_verified_at: Optional[datetime] = None
    kyc_verified_by: Optional[int] = None
    kyc_rejection_reason: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# -----------------------------
# Token Schemas
# -----------------------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

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

# -----------------------------
# Audit Trail Schemas
# -----------------------------
class UserProfileChangeOut(BaseModel):
    id: int
    user_id: int
    changed_by: int
    field_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    change_type: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# -----------------------------
# KYC Schemas
# -----------------------------
class KYCVerificationRequest(BaseModel):
    business_name: str
    business_registration_number: str
    business_tax_id: str
    business_type: BusinessType
    business_industry: str
    business_description: str
    business_phones: List[str] = Field(..., min_items=1, max_items=4)
    business_emails: List[str] = Field(..., min_items=1, max_items=5)
    business_addresses: List[BusinessAddress] = Field(..., min_items=1, max_items=3)
    bank_accounts: List[BankAccount] = Field(..., min_items=1, max_items=3)
    
    model_config = ConfigDict(extra="forbid")

class KYCVerificationResponse(BaseModel):
    status: KYCStatus
    message: str
    estimated_processing_time: Optional[str] = None