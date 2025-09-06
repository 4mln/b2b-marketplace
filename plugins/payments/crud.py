from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from .models import Payment, PaymentStatus, PaymentType, PaymentRefund, PaymentWebhook, WithdrawalRequest
from .schemas import PaymentCreate, PaymentUpdate

# -----------------------------
# Payment CRUD Operations
# -----------------------------
async def create_payment(db: AsyncSession, payment_data: Dict[str, Any]) -> Payment:
    """Create a new payment record"""
    payment = Payment(**payment_data)
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return payment

async def get_payment(db: AsyncSession, payment_id: int) -> Optional[Payment]:
    """Get payment by ID"""
    return await db.get(Payment, payment_id)

async def get_payment_by_reference(db: AsyncSession, reference_id: str) -> Optional[Payment]:
    """Get payment by reference ID"""
    result = await db.execute(
        select(Payment).where(Payment.reference_id == reference_id)
    )
    return result.scalars().first()

async def update_payment_status(
    db: AsyncSession, 
    payment_id: int, 
    status: PaymentStatus,
    provider_error: Optional[str] = None,
    provider_transaction_id: Optional[str] = None,
    provider_response: Optional[Dict[str, Any]] = None
) -> Optional[Payment]:
    """Update payment status and related fields"""
    update_data = {
        "status": status,
        "updated_at": datetime.utcnow()
    }
    
    if provider_error is not None:
        update_data["provider_error"] = provider_error
    
    if provider_transaction_id is not None:
        update_data["provider_transaction_id"] = provider_transaction_id
    
    if provider_response is not None:
        update_data["provider_response"] = provider_response
    
    if status == PaymentStatus.COMPLETED:
        update_data["completed_at"] = datetime.utcnow()
    
    await db.execute(
        update(Payment)
        .where(Payment.id == payment_id)
        .values(**update_data)
    )
    await db.commit()
    
    return await get_payment(db, payment_id)

async def list_user_payments(
    db: AsyncSession,
    user_id: int,
    page: int = 1,
    page_size: int = 10,
    status: Optional[PaymentStatus] = None,
    payment_type: Optional[PaymentType] = None
) -> List[Payment]:
    """Get user's payment history with pagination and filters"""
    query = select(Payment).where(Payment.user_id == user_id)
    
    if status:
        query = query.where(Payment.status == status)
    
    if payment_type:
        query = query.where(Payment.payment_type == payment_type)
    
    # Order by created_at descending
    query = query.order_by(Payment.created_at.desc())
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_payment_statistics(
    db: AsyncSession,
    user_id: int,
    days: int = 30
) -> Dict[str, Any]:
    """Get payment statistics for a user"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get all payments in the date range
    result = await db.execute(
        select(Payment)
        .where(Payment.user_id == user_id)
        .where(Payment.created_at >= start_date)
    )
    payments = result.scalars().all()
    
    total_payments = len(payments)
    total_amount = sum(p.amount for p in payments if p.status == PaymentStatus.COMPLETED)
    successful_payments = len([p for p in payments if p.status == PaymentStatus.COMPLETED])
    failed_payments = len([p for p in payments if p.status == PaymentStatus.FAILED])
    
    # Group by provider
    provider_stats = {}
    for payment in payments:
        provider = payment.payment_method
        if provider not in provider_stats:
            provider_stats[provider] = {"count": 0, "amount": 0, "successful": 0}
        
        provider_stats[provider]["count"] += 1
        if payment.status == PaymentStatus.COMPLETED:
            provider_stats[provider]["amount"] += payment.amount
            provider_stats[provider]["successful"] += 1
    
    # Calculate success rates
    for provider in provider_stats:
        stats = provider_stats[provider]
        stats["success_rate"] = (stats["successful"] / stats["count"] * 100) if stats["count"] > 0 else 0
    
    return {
        "total_payments": total_payments,
        "total_amount": total_amount,
        "successful_payments": successful_payments,
        "failed_payments": failed_payments,
        "success_rate": (successful_payments / total_payments * 100) if total_payments > 0 else 0,
        "provider_statistics": provider_stats,
        "period_days": days
    }

# -----------------------------
# Withdrawal Requests
# -----------------------------
async def create_withdrawal_request(db: AsyncSession, user_id: int, amount: float, currency: str, bank_account: Dict[str, Any]) -> WithdrawalRequest:
    req = WithdrawalRequest(user_id=user_id, amount=amount, currency=currency, bank_account=bank_account)
    db.add(req)
    await db.commit()
    await db.refresh(req)
    return req

async def list_withdrawal_requests(db: AsyncSession, user_id: int | None = None) -> List[WithdrawalRequest]:
    query = select(WithdrawalRequest)
    if user_id:
        query = query.where(WithdrawalRequest.user_id == user_id)
    result = await db.execute(query.order_by(WithdrawalRequest.created_at.desc()))
    return result.scalars().all()

async def update_withdrawal_status(db: AsyncSession, request_id: int, status: str, reason: str | None = None) -> WithdrawalRequest | None:
    req = await db.get(WithdrawalRequest, request_id)
    if not req:
        return None
    req.status = status
    if reason:
        req.reason = reason
    req.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(req)
    return req

# -----------------------------
# Payment Callback Processing
# -----------------------------
async def process_payment_callback(
    db: AsyncSession,
    provider_name: str,
    body: bytes,
    headers: Dict[str, str]
) -> Dict[str, Any]:
    """Process payment callback from provider"""
    try:
        # Parse callback data based on provider
        callback_data = parse_provider_callback(provider_name, body, headers)
        
        if not callback_data:
            return {"success": False, "error": "Invalid callback data"}
        
        # Find payment by reference ID
        payment = await get_payment_by_reference(db, callback_data["reference_id"])
        if not payment:
            return {"success": False, "error": "Payment not found"}
        
        # Verify callback signature if provided
        if callback_data.get("signature"):
            if not verify_callback_signature(provider_name, body, callback_data["signature"]):
                return {"success": False, "error": "Invalid signature"}
        
        # Update payment status based on provider response
        if callback_data["status"] == "success":
            await update_payment_status(
                db,
                payment.id,
                PaymentStatus.COMPLETED,
                provider_transaction_id=callback_data.get("transaction_id"),
                provider_response=callback_data
            )
        else:
            await update_payment_status(
                db,
                payment.id,
                PaymentStatus.FAILED,
                provider_error=callback_data.get("error_message", "Payment failed"),
                provider_response=callback_data
            )
        
        # Log webhook
        await log_payment_webhook(db, provider_name, "payment_callback", callback_data)
        
        return {"success": True, "payment": payment}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def parse_provider_callback(provider_name: str, body: bytes, headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Parse callback data based on provider"""
    import json
    
    try:
        data = json.loads(body.decode('utf-8'))
        
        if provider_name == "zarinpal":
            return parse_zarinpal_callback(data)
        elif provider_name == "payping":
            return parse_payping_callback(data)
        elif provider_name == "idpay":
            return parse_idpay_callback(data)
        elif provider_name == "parsijoo":
            return parse_parsijoo_callback(data)
        else:
            # Generic callback parsing
            return {
                "status": data.get("status", "unknown"),
                "reference_id": data.get("reference_id") or data.get("order_id"),
                "transaction_id": data.get("transaction_id") or data.get("ref_id"),
                "amount": data.get("amount"),
                "error_message": data.get("error_message")
            }
    except Exception as e:
        return None

def parse_zarinpal_callback(data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse ZarinPal callback data"""
    return {
        "status": "success" if data.get("Status") == "OK" else "failed",
        "reference_id": data.get("Authority"),
        "transaction_id": data.get("RefID"),
        "amount": data.get("Amount"),
        "error_message": data.get("error_message")
    }

def parse_payping_callback(data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse Payping callback data"""
    return {
        "status": "success" if data.get("status") == "success" else "failed",
        "reference_id": data.get("clientRefId"),
        "transaction_id": data.get("refNum"),
        "amount": data.get("amount"),
        "error_message": data.get("message")
    }

def parse_idpay_callback(data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse IDPay callback data"""
    return {
        "status": "success" if data.get("status") == 200 else "failed",
        "reference_id": data.get("order_id"),
        "transaction_id": data.get("id"),
        "amount": data.get("amount"),
        "error_message": data.get("error_message")
    }

def parse_parsijoo_callback(data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse Parsijoo callback data"""
    return {
        "status": "success" if data.get("status") == "success" else "failed",
        "reference_id": data.get("order_id"),
        "transaction_id": data.get("payment_id"),
        "amount": data.get("amount"),
        "error_message": data.get("message")
    }

def verify_callback_signature(provider_name: str, body: bytes, signature: str) -> bool:
    """Verify callback signature"""
    # In a real implementation, you would verify the signature
    # For now, return True (implement proper verification for production)
    return True

async def log_payment_webhook(
    db: AsyncSession,
    provider_name: str,
    event_type: str,
    payload: Dict[str, Any]
) -> PaymentWebhook:
    """Log payment webhook for audit trail"""
    webhook = PaymentWebhook(
        provider_name=provider_name,
        event_type=event_type,
        payload=payload
    )
    db.add(webhook)
    await db.commit()
    await db.refresh(webhook)
    return webhook

# -----------------------------
# Payment Refund Operations
# -----------------------------
async def create_payment_refund(
    db: AsyncSession,
    payment_id: int,
    amount: float,
    reason: Optional[str] = None
) -> PaymentRefund:
    """Create a payment refund"""
    refund = PaymentRefund(
        payment_id=payment_id,
        amount=amount,
        reason=reason
    )
    db.add(refund)
    await db.commit()
    await db.refresh(refund)
    return refund

async def update_refund_status(
    db: AsyncSession,
    refund_id: int,
    status: PaymentStatus,
    provider_refund_id: Optional[str] = None
) -> Optional[PaymentRefund]:
    """Update refund status"""
    update_data = {
        "status": status,
        "processed_at": datetime.utcnow() if status == PaymentStatus.COMPLETED else None
    }
    
    if provider_refund_id:
        update_data["provider_refund_id"] = provider_refund_id
    
    await db.execute(
        update(PaymentRefund)
        .where(PaymentRefund.id == refund_id)
        .values(**update_data)
    )
    await db.commit()
    
    return await db.get(PaymentRefund, refund_id)

# -----------------------------
# Optional init hook used by plugin loader
# -----------------------------
async def init_tables(engine=None):
    """Optional no-op initializer to satisfy plugin loader if called."""
    return True

# -----------------------------
# Payment Analytics
# -----------------------------
async def get_payment_analytics(
    db: AsyncSession,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """Get payment analytics for admin dashboard"""
    
    # Get payments in date range
    result = await db.execute(
        select(Payment)
        .where(Payment.created_at >= start_date)
        .where(Payment.created_at <= end_date)
    )
    payments = result.scalars().all()
    
    # Calculate metrics
    total_payments = len(payments)
    total_amount = sum(p.amount for p in payments if p.status == PaymentStatus.COMPLETED)
    successful_payments = len([p for p in payments if p.status == PaymentStatus.COMPLETED])
    failed_payments = len([p for p in payments if p.status == PaymentStatus.FAILED])
    
    # Group by payment type
    type_stats = {}
    for payment in payments:
        payment_type = payment.payment_type
        if payment_type not in type_stats:
            type_stats[payment_type] = {"count": 0, "amount": 0}
        
        type_stats[payment_type]["count"] += 1
        if payment.status == PaymentStatus.COMPLETED:
            type_stats[payment_type]["amount"] += payment.amount
    
    # Group by provider
    provider_stats = {}
    for payment in payments:
        provider = payment.payment_method
        if provider not in provider_stats:
            provider_stats[provider] = {"count": 0, "amount": 0, "successful": 0}
        
        provider_stats[provider]["count"] += 1
        if payment.status == PaymentStatus.COMPLETED:
            provider_stats[provider]["amount"] += payment.amount
            provider_stats[provider]["successful"] += 1
    
    return {
        "total_payments": total_payments,
        "total_amount": total_amount,
        "successful_payments": successful_payments,
        "failed_payments": failed_payments,
        "success_rate": (successful_payments / total_payments * 100) if total_payments > 0 else 0,
        "type_statistics": type_stats,
        "provider_statistics": provider_stats,
        "period": {
            "start_date": start_date,
            "end_date": end_date
        }
    }
