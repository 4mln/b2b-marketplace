"""
Internationalization (i18n) Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class Direction(str, Enum):
    LTR = "ltr"
    RTL = "rtl"


# Language Schemas
class LanguageBase(BaseModel):
    code: str = Field(..., max_length=10)
    name: str = Field(..., max_length=100)
    native_name: str = Field(..., max_length=100)
    is_rtl: bool = False
    is_active: bool = True
    is_default: bool = False


class LanguageCreate(LanguageBase):
    pass


class LanguageUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    native_name: Optional[str] = Field(None, max_length=100)
    is_rtl: Optional[bool] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class LanguageOut(LanguageBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Translation Schemas
class TranslationBase(BaseModel):
    key: str = Field(..., max_length=255)
    value: str
    context: Optional[str] = Field(None, max_length=100)
    is_active: bool = True


class TranslationCreate(TranslationBase):
    language_id: int


class TranslationUpdate(BaseModel):
    value: Optional[str] = None
    context: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class TranslationOut(TranslationBase):
    id: int
    language_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Currency Schemas
class CurrencyBase(BaseModel):
    code: str = Field(..., max_length=10)
    name: str = Field(..., max_length=100)
    symbol: str = Field(..., max_length=10)
    is_active: bool = True
    is_default: bool = False
    exchange_rate: int = 1


class CurrencyCreate(CurrencyBase):
    pass


class CurrencyUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    symbol: Optional[str] = Field(None, max_length=10)
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    exchange_rate: Optional[int] = None


class CurrencyOut(CurrencyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Timezone Schemas
class TimezoneBase(BaseModel):
    name: str = Field(..., max_length=100)
    offset: str = Field(..., max_length=10)
    is_active: bool = True
    is_default: bool = False


class TimezoneCreate(TimezoneBase):
    pass


class TimezoneUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    offset: Optional[str] = Field(None, max_length=10)
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class TimezoneOut(TimezoneBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Date Format Schemas
class DateFormatBase(BaseModel):
    name: str = Field(..., max_length=100)
    format_string: str = Field(..., max_length=50)
    is_rtl: bool = False
    is_active: bool = True
    is_default: bool = False


class DateFormatCreate(DateFormatBase):
    pass


class DateFormatUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    format_string: Optional[str] = Field(None, max_length=50)
    is_rtl: Optional[bool] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class DateFormatOut(DateFormatBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# User Preference Schemas
class UserLanguagePreferenceBase(BaseModel):
    language_id: int
    is_primary: bool = True


class UserLanguagePreferenceCreate(UserLanguagePreferenceBase):
    pass


class UserLanguagePreferenceOut(UserLanguagePreferenceBase):
    id: int
    user_id: int
    created_at: datetime
    language: LanguageOut
    
    class Config:
        from_attributes = True


class UserCurrencyPreferenceBase(BaseModel):
    currency_id: int
    is_primary: bool = True


class UserCurrencyPreferenceCreate(UserCurrencyPreferenceBase):
    pass


class UserCurrencyPreferenceOut(UserCurrencyPreferenceBase):
    id: int
    user_id: int
    created_at: datetime
    currency: CurrencyOut
    
    class Config:
        from_attributes = True


class UserTimezonePreferenceBase(BaseModel):
    timezone_id: int


class UserTimezonePreferenceCreate(UserTimezonePreferenceBase):
    pass


class UserTimezonePreferenceOut(UserTimezonePreferenceBase):
    id: int
    user_id: int
    created_at: datetime
    timezone: TimezoneOut
    
    class Config:
        from_attributes = True


class UserDateFormatPreferenceBase(BaseModel):
    date_format_id: int


class UserDateFormatPreferenceCreate(UserDateFormatPreferenceBase):
    pass


class UserDateFormatPreferenceOut(UserDateFormatPreferenceBase):
    id: int
    user_id: int
    created_at: datetime
    date_format: DateFormatOut
    
    class Config:
        from_attributes = True


# Response Schemas
class LanguageListResponse(BaseModel):
    languages: List[LanguageOut]
    total: int


class TranslationListResponse(BaseModel):
    translations: List[TranslationOut]
    total: int
    page: int
    page_size: int


class CurrencyListResponse(BaseModel):
    currencies: List[CurrencyOut]
    total: int


class TimezoneListResponse(BaseModel):
    timezones: List[TimezoneOut]
    total: int


class DateFormatListResponse(BaseModel):
    date_formats: List[DateFormatOut]
    total: int


# User Preferences Response
class UserPreferencesOut(BaseModel):
    language: Optional[UserLanguagePreferenceOut] = None
    currency: Optional[UserCurrencyPreferenceOut] = None
    timezone: Optional[UserTimezonePreferenceOut] = None
    date_format: Optional[UserDateFormatPreferenceOut] = None


# Translation Request/Response
class TranslationRequest(BaseModel):
    keys: List[str]
    language_code: str
    context: Optional[str] = None


class TranslationResponse(BaseModel):
    translations: Dict[str, str]
    language_code: str


# Format Schemas
class DateFormatRequest(BaseModel):
    date: datetime
    format_type: str = "jalali"  # jalali, gregorian
    language_code: str = "fa"


class DateFormatResponse(BaseModel):
    formatted_date: str
    original_date: datetime
    format_type: str
    language_code: str


class CurrencyFormatRequest(BaseModel):
    amount: float
    currency_code: str = "IRR"
    language_code: str = "fa"


class CurrencyFormatResponse(BaseModel):
    formatted_amount: str
    original_amount: float
    currency_code: str
    currency_symbol: str
    language_code: str


# System Configuration
class SystemLocaleConfig(BaseModel):
    default_language: str = "fa"
    default_currency: str = "IRR"
    default_timezone: str = "Asia/Tehran"
    default_date_format: str = "jalali"
    supported_languages: List[str] = ["fa", "en", "ar"]
    supported_currencies: List[str] = ["IRR", "USD", "EUR"]
    rtl_languages: List[str] = ["fa", "ar"]


