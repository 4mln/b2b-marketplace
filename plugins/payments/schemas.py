from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

# -----------------------------
# Payment Enums
# -----------------------------
class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentMethod(str, Enum):
    # Iran Local Payment Methods
    ZARINPAL = "zarinpal"
    MELLAT = "mellat"
    PARSIJOO = "parsijoo"
    PAYPING = "payping"
    IDPAY = "idpay"
    NEXT_PAY = "next_pay"
    
    # International Payment Methods
    STRIPE = "stripe"
    PAYPAL = "paypal"
    
    # Crypto (Future)
    BITCOIN = "bitcoin"
    ETHEREUM = "ethereum"
    TETHER = "tether"

class PaymentType(str, Enum):
    WALLET_TOPUP = "wallet_topup"
    SUBSCRIPTION = "subscription"
    AD_PAYMENT = "ad_payment"
    ORDER_PAYMENT = "order_payment"
    ESCROW_PAYMENT = "escrow_payment"
    REFUND = "refund"

# -----------------------------
# Payment Schemas
# -----------------------------
class PaymentBase(BaseModel):
    amount: float = Field(..., gt=0, description="Payment amount")
    currency: str = Field("IRR", description="Currency code")
    payment_method: PaymentMethod
    payment_type: PaymentType
    description: Optional[str] = None
    reference_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PaymentCreate(PaymentBase):
    user_id: int
    model_config = {"extra": "forbid"}

class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    provider_transaction_id: Optional[str] = None
    provider_response: Optional[Dict[str, Any]] = None
    provider_error: Optional[str] = None
    completed_at: Optional[datetime] = None
    model_config = {"extra": "forbid"}

class PaymentOut(PaymentBase):
    id: int
    user_id: int
    status: PaymentStatus
    provider_transaction_id: Optional[str] = None
    provider_response: Optional[Dict[str, Any]] = None
    provider_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}

# -----------------------------
# Wallet Top-up Schemas
# -----------------------------
class WalletTopupRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Top-up amount")
    currency: str = Field("IRR", description="Currency code")
    provider: PaymentMethod = Field(..., description="Payment provider")
    model_config = {"extra": "forbid"}

class WalletTopupResponse(BaseModel):
    payment: PaymentOut
    payment_url: str
    authority: Optional[str] = None  # For ZarinPal
    code: Optional[str] = None  # For Payping
    id: Optional[str] = None  # For IDPay

# -----------------------------
# Payment Verification Schemas
# -----------------------------
class PaymentVerification(BaseModel):
    payment_id: int
    authority: Optional[str] = None  # For ZarinPal
    transaction_id: Optional[str] = None  # For other providers
    model_config = {"extra": "forbid"}

class PaymentCallback(BaseModel):
    provider: str
    status: str
    transaction_id: Optional[str] = None
    authority: Optional[str] = None
    amount: Optional[float] = None
    reference_id: Optional[str] = None
    signature: Optional[str] = None
    payload: Dict[str, Any]

# -----------------------------
# Payment Provider Schemas
# -----------------------------
class PaymentProviderInfo(BaseModel):
    name: str
    display_name: str
    description: str
    supports_irr: bool
    supports_usd: bool
    supports_eur: bool
    transaction_fee_percentage: float
    minimum_amount: float
    logo_url: Optional[str] = None

class PaymentProviderConfig(BaseModel):
    api_key: str
    merchant_id: Optional[str] = None
    terminal_id: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    callback_url: str
    webhook_url: Optional[str] = None
    is_test_mode: bool = True

# -----------------------------
# Payment Statistics Schemas
# -----------------------------
class PaymentStatistics(BaseModel):
    total_payments: int
    total_amount: float
    successful_payments: int
    failed_payments: int
    success_rate: float
    provider_statistics: Dict[str, Dict[str, Any]]
    period_days: int

class PaymentProviderStats(BaseModel):
    provider: str
    count: int
    amount: float
    success_rate: float

# -----------------------------
# Withdrawal Schemas
# -----------------------------
class WithdrawalRequestCreate(BaseModel):
    amount: float = Field(..., gt=0)
    currency: str = Field("IRR")
    bank_account: Dict[str, Any]
    model_config = {"extra": "forbid"}

class WithdrawalRequestOut(BaseModel):
    id: int
    user_id: int
    amount: float
    currency: str
    bank_account: Dict[str, Any]
    status: str
    reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}

# -----------------------------
# Payment Refund Schemas
# -----------------------------
class PaymentRefundRequest(BaseModel):
    payment_id: int
    amount: float = Field(..., gt=0, description="Refund amount")
    reason: Optional[str] = None
    model_config = {"extra": "forbid"}

class PaymentRefundOut(BaseModel):
    id: int
    payment_id: int
    amount: float
    reason: Optional[str] = None
    status: PaymentStatus
    provider_refund_id: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}

# -----------------------------
# Payment Webhook Schemas
# -----------------------------
class PaymentWebhookOut(BaseModel):
    id: int
    provider_name: str
    event_type: str
    payload: Dict[str, Any]
    signature: Optional[str] = None
    processed: bool
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    
    model_config = {"from_attributes": True}

# -----------------------------
# Payment Fee Schemas
# -----------------------------
class PaymentFeeCalculation(BaseModel):
    amount: float
    fee_percentage: float
    fee_amount: float
    total_amount: float

class PaymentFeeResponse(BaseModel):
    success: bool
    fees: PaymentFeeCalculation
    provider: str
    currency: str

# -----------------------------
# Payment Error Schemas
# -----------------------------
class PaymentError(BaseModel):
    error_code: str
    error_message: str
    provider: str
    transaction_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# -----------------------------
# Payment History Schemas
# -----------------------------
class PaymentHistoryRequest(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)
    status: Optional[PaymentStatus] = None
    payment_type: Optional[PaymentType] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    provider: Optional[PaymentMethod] = None

class PaymentHistoryResponse(BaseModel):
    payments: List[PaymentOut]
    total: int
    page: int
    page_size: int
    total_pages: int 