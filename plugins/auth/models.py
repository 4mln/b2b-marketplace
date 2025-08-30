from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    kyc_status = Column(String, default="pending", nullable=False)  # pending, otp_verified, business_verified, rejected
    otp_code = Column(String, nullable=True)
    otp_expiry = Column(DateTime, nullable=True)
    id_document = Column(String, nullable=True)  # Path to uploaded ID document
    role = Column(String, default="user", nullable=False)  # user, seller, buyer, both
    
    # Business Information
    business_name = Column(String, nullable=True)
    business_registration_number = Column(String, nullable=True)
    business_tax_id = Column(String, nullable=True)
    business_type = Column(String, nullable=True)  # individual, company, partnership
    business_industry = Column(String, nullable=True)
    business_description = Column(Text, nullable=True)
    
    # Contact Details
    business_phones = Column(JSON, nullable=True)  # Array of up to 4 phone numbers
    business_emails = Column(JSON, nullable=True)  # Array of business emails
    website = Column(String, nullable=True)
    telegram_id = Column(String, nullable=True)
    whatsapp_id = Column(String, nullable=True)
    
    # Addresses (up to 3 different addresses)
    business_addresses = Column(JSON, nullable=True)  # Array of address objects
    
    # Bank Accounts (up to 3 different accounts)
    bank_accounts = Column(JSON, nullable=True)  # Array of bank account objects
    
    # Media
    business_photo = Column(String, nullable=True)  # Path to business photo
    banner_photo = Column(String, nullable=True)  # Path to banner photo
    
    # Privacy & Preferences
    privacy_settings = Column(JSON, nullable=True)  # Privacy control settings
    notification_preferences = Column(JSON, nullable=True)  # Notification preferences
    
    # Audit Trail
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    profile_completion_percentage = Column(Integer, default=0)  # 0-100
    
    # KYC & Verification
    kyc_verified_at = Column(DateTime, nullable=True)
    kyc_verified_by = Column(Integer, nullable=True)  # Admin user ID
    kyc_rejection_reason = Column(Text, nullable=True)
    
    # Relationships
    sellers = relationship(
        "Seller",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    buyer = relationship(
        "Buyer",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False
    )
    
    wallets = relationship(
        "Wallet",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # Audit trail relationship
    profile_changes = relationship(
        "UserProfileChange",
        back_populates="user",
        cascade="all, delete-orphan"
    )

class UserProfileChange(Base):
    """Audit trail for user profile changes"""
    __tablename__ = "user_profile_changes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    changed_by = Column(Integer, nullable=False)  # User ID who made the change
    field_name = Column(String, nullable=False)  # Name of the field that changed
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    change_type = Column(String, nullable=False)  # create, update, delete
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="profile_changes")