"""
Internationalization (i18n) Models
Supports Persian/RTL and multiple languages
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.db.base import Base


class Language(Base):
    """Supported languages"""
    __tablename__ = "languages"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False)  # e.g., 'fa', 'en', 'ar'
    name = Column(String(100), nullable=False)  # e.g., 'Persian', 'English', 'Arabic'
    native_name = Column(String(100), nullable=False)  # e.g., 'فارسی', 'English', 'العربية'
    is_rtl = Column(Boolean, default=False)  # Right-to-left support
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    translations = relationship("Translation", back_populates="language")


class Translation(Base):
    """Translation strings for different languages"""
    __tablename__ = "translations"
    
    id = Column(Integer, primary_key=True, index=True)
    language_id = Column(Integer, ForeignKey("languages.id"), nullable=False)
    key = Column(String(255), nullable=False)  # Translation key
    value = Column(Text, nullable=False)  # Translated text
    context = Column(String(100), nullable=True)  # Context for disambiguation
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    language = relationship("Language", back_populates="translations")


class UserLanguagePreference(Base):
    """User language preferences"""
    __tablename__ = "user_language_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    language_id = Column(Integer, ForeignKey("languages.id"), nullable=False)
    is_primary = Column(Boolean, default=True)  # Primary language preference
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    language = relationship("Language")


class Currency(Base):
    """Supported currencies"""
    __tablename__ = "currencies"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False)  # e.g., 'IRR', 'USD', 'EUR'
    name = Column(String(100), nullable=False)  # e.g., 'Iranian Rial', 'US Dollar'
    symbol = Column(String(10), nullable=False)  # e.g., 'ریال', '$', '€'
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    exchange_rate = Column(Integer, default=1)  # Exchange rate to base currency
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class UserCurrencyPreference(Base):
    """User currency preferences"""
    __tablename__ = "user_currency_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    is_primary = Column(Boolean, default=True)  # Primary currency preference
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    currency = relationship("Currency")


class Timezone(Base):
    """Supported timezones"""
    __tablename__ = "timezones"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # e.g., 'Asia/Tehran', 'UTC'
    offset = Column(String(10), nullable=False)  # e.g., '+03:30', '+00:00'
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserTimezonePreference(Base):
    """User timezone preferences"""
    __tablename__ = "user_timezone_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    timezone_id = Column(Integer, ForeignKey("timezones.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    timezone = relationship("Timezone")


class DateFormat(Base):
    """Date format preferences"""
    __tablename__ = "date_formats"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # e.g., 'Jalali', 'Gregorian'
    format_string = Column(String(50), nullable=False)  # e.g., '%Y/%m/%d', '%d/%m/%Y'
    is_rtl = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserDateFormatPreference(Base):
    """User date format preferences"""
    __tablename__ = "user_date_format_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date_format_id = Column(Integer, ForeignKey("date_formats.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    date_format = relationship("DateFormat")
