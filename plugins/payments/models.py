
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, Enum, JSON
from sqlalchemy.orm import relationship
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
    ZARINPAL = "zarinpal"
    MELLAT = "mellat"
    PARSIJOO = "parsijoo"
    PAYPING = "payping"
    IDPAY = "idpay"
    NEXT_PAY = "next_pay"
    STRIPE = "stripe"
    PAYPAL = "paypal"
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
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="IRR")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_type = Column(Enum(PaymentType), nullable=False)
    reference_id = Column(String, nullable=True, index=True)
    provider_transaction_id = Column(String, nullable=True)
    provider_response = Column(JSON, nullable=True)
    provider_error = Column(String, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    order = relationship("Order", back_populates="payments")
    user = relationship("User")


class PaymentRefund(Base):
    __tablename__ = "payment_refunds"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    amount = Column(Float, nullable=False)
    reason = Column(String, nullable=True)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    provider_refund_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

    payment = relationship("Payment")


class PaymentWebhook(Base):
    __tablename__ = "payment_webhooks"

    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    signature = Column(String, nullable=True)
    processed = Column(Integer, default=0)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WithdrawalRequest(Base):
    __tablename__ = "withdrawal_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="IRR")
    bank_account = Column(JSON, nullable=False)
    status = Column(String, default="pending")
    reason = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)
