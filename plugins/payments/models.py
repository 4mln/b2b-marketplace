from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Boolean, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentMethod(str, enum.Enum):
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

class PaymentType(str, enum.Enum):
    WALLET_TOPUP = "wallet_topup"
    SUBSCRIPTION = "subscription"
    AD_PAYMENT = "ad_payment"
    ORDER_PAYMENT = "order_payment"
    ESCROW_PAYMENT = "escrow_payment"
    REFUND = "refund"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="IRR")  # IRR, USD, EUR
    payment_method = Column(String, nullable=False)
    payment_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default=PaymentStatus.PENDING)
    
    # Payment provider specific fields
    provider_transaction_id = Column(String, nullable=True)  # External transaction ID
    provider_response = Column(JSON, nullable=True)  # Full provider response
    provider_error = Column(Text, nullable=True)  # Error message from provider
    
    # Payment metadata
    description = Column(Text, nullable=True)
    reference_id = Column(String, nullable=True)  # Reference to order, subscription, etc.
    metadata = Column(JSON, nullable=True)  # Additional payment metadata
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="payments")
    refunds = relationship("PaymentRefund", back_populates="payment", cascade="all, delete-orphan")

class PaymentRefund(Base):
    __tablename__ = "payment_refunds"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    amount = Column(Float, nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(String, nullable=False, default=PaymentStatus.PENDING)
    provider_refund_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    payment = relationship("Payment", back_populates="refunds")

class PaymentProvider(Base):
    __tablename__ = "payment_providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    display_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_test_mode = Column(Boolean, default=True)
    
    # Provider configuration
    api_key = Column(String, nullable=True)
    api_secret = Column(String, nullable=True)
    merchant_id = Column(String, nullable=True)
    callback_url = Column(String, nullable=True)
    webhook_url = Column(String, nullable=True)
    
    # Supported features
    supports_irr = Column(Boolean, default=True)
    supports_usd = Column(Boolean, default=False)
    supports_eur = Column(Boolean, default=False)
    supports_refunds = Column(Boolean, default=True)
    
    # Fee structure
    transaction_fee_percentage = Column(Float, default=0.0)
    transaction_fee_fixed = Column(Float, default=0.0)
    minimum_amount = Column(Float, default=0.0)
    maximum_amount = Column(Float, nullable=True)
    
    # Configuration
    config = Column(JSON, nullable=True)  # Provider-specific configuration
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PaymentWebhook(Base):
    __tablename__ = "payment_webhooks"

    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    signature = Column(String, nullable=True)
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)