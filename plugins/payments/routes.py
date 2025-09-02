from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from datetime import datetime

from app.db.session import get_session
from plugins.user.security import get_current_user
from plugins.auth.models import User
from plugins.payments.models import Payment, PaymentStatus, PaymentMethod, PaymentType
from plugins.payments.iran_providers import IranPaymentFactory, get_available_providers, calculate_payment_fees
from plugins.payments.schemas import (
    PaymentCreate, PaymentOut, PaymentCallback, PaymentVerification,
    WalletTopupRequest, PaymentProviderInfo
)
from plugins.payments.crud import (
    create_payment, get_payment, update_payment_status,
    list_user_payments, process_payment_callback
)
from plugins.wallet.crud import get_user_wallet_by_currency, deposit
from sqlalchemy import select
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

router = APIRouter()

# -----------------------------
# Get Available Payment Providers
# -----------------------------
@router.get("/providers", response_model=Dict[str, PaymentProviderInfo], operation_id="get_payment_providers")
async def get_payment_providers():
    """Get list of available payment providers"""
    providers = await get_available_providers()
    return providers

# -----------------------------
# Calculate Payment Fees
# -----------------------------
@router.get("/fees", operation_id="calculate_payment_fees")
async def calculate_fees(
    amount: float = Query(..., gt=0, description="Payment amount"),
    provider: str = Query(..., description="Payment provider name"),
    currency: str = Query("IRR", description="Currency code")
):
    """Calculate payment fees for a given amount and provider"""
    try:
        fees = await calculate_payment_fees(amount, provider)
        return {
            "success": True,
            "fees": fees,
            "provider": provider,
            "currency": currency
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# -----------------------------
# Create Payment (Wallet Top-up)
# -----------------------------
@router.post("/wallet/topup", response_model=PaymentOut, operation_id="wallet_topup")
async def wallet_topup(
    topup_request: WalletTopupRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Top up wallet using Iran payment providers"""
    
    # Validate amount
    if topup_request.amount < 1000:  # Minimum 1000 IRR
        raise HTTPException(status_code=400, detail="Minimum amount is 1000 IRR")
    
    # Get user's wallet for the currency
    wallet = await get_user_wallet_by_currency(db, current_user.id, topup_request.currency)
    if not wallet:
        raise HTTPException(status_code=404, detail=f"No wallet found for currency {topup_request.currency}")
    
    # Calculate fees
    try:
        fees = await calculate_payment_fees(topup_request.amount, topup_request.provider)
        total_amount = fees["total_amount"]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Create payment record
    payment_data = {
        "user_id": current_user.id,
        "amount": total_amount,
        "currency": topup_request.currency,
        "payment_method": topup_request.provider,
        "payment_type": PaymentType.WALLET_TOPUP,
        "description": f"Wallet top-up: {topup_request.amount} {topup_request.currency}",
        "reference_id": f"topup_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "metadata": {
            "wallet_id": wallet.id,
            "original_amount": topup_request.amount,
            "fee_amount": fees["fee_amount"],
            "fee_percentage": fees["fee_percentage"]
        }
    }
    
    payment = await create_payment(db, payment_data)
    
    # Get provider configuration
    provider_config = {
        "api_key": get_provider_api_key(topup_request.provider),
        "merchant_id": get_provider_merchant_id(topup_request.provider),
        "callback_url": f"/api/payments/callback/{topup_request.provider}",
        "is_test_mode": True  # Set to False in production
    }
    
    # Create payment with provider
    provider = IranPaymentFactory.create_provider(topup_request.provider, provider_config)
    provider_result = await provider.create_payment(
        amount=total_amount,
        currency=topup_request.currency,
        description=payment_data["description"],
        reference_id=payment.reference_id,
        user_phone=current_user.phone
    )
    
    if not provider_result["success"]:
        # Update payment status to failed
        await update_payment_status(db, payment.id, PaymentStatus.FAILED, provider_result["error"])
        raise HTTPException(status_code=400, detail=provider_result["error"])
    
    # Update payment with provider response
    await update_payment_status(
        db, 
        payment.id, 
        PaymentStatus.PROCESSING,
        provider_response=provider_result["provider_response"]
    )
    
    return PaymentOut.model_validate(payment)

# -----------------------------
# Payment Callback (Provider Webhook)
# -----------------------------
@router.post("/callback/{provider_name}", operation_id="payment_callback")
async def payment_callback(
    provider_name: str,
    request: Request,
    db: AsyncSession = Depends(get_session)
):
    """Handle payment callbacks from providers"""
    
    # Get request body
    body = await request.body()
    headers = dict(request.headers)
    
    # Process callback based on provider
    try:
        result = await process_payment_callback(db, provider_name, body, headers)
        
        if result["success"]:
            # If payment is successful, top up wallet
            payment = result["payment"]
            if payment.payment_type == PaymentType.WALLET_TOPUP:
                wallet = await get_user_wallet_by_currency(db, payment.user_id, payment.currency)
                if wallet:
                    await deposit(db, wallet.id, payment.amount, "Wallet top-up via payment gateway")
            
            return {"status": "success", "message": "Payment processed successfully"}
        else:
            return {"status": "error", "message": result["error"]}
            
    except Exception as e:
        logger.error(f"Payment callback error: {e}")
        return {"status": "error", "message": "Internal server error"}

# -----------------------------
# Verify Payment
# -----------------------------
@router.post("/verify", operation_id="verify_payment")
async def verify_payment(
    verification: PaymentVerification,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Verify payment with provider"""
    
    # Get payment record
    payment = await get_payment(db, verification.payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to verify this payment")
    
    # Get provider configuration
    provider_config = {
        "api_key": get_provider_api_key(payment.payment_method),
        "merchant_id": get_provider_merchant_id(payment.payment_method),
        "callback_url": f"/api/payments/callback/{payment.payment_method}",
        "is_test_mode": True
    }
    
    # Verify with provider
    provider = IranPaymentFactory.create_provider(payment.payment_method, provider_config)
    
    # Get verification parameters based on provider
    if payment.payment_method == "zarinpal":
        verify_result = await provider.verify_payment(verification.authority, payment.amount)
    else:
        verify_result = await provider.verify_payment(verification.transaction_id, payment.amount)
    
    if verify_result["success"]:
        # Update payment status
        await update_payment_status(
            db, 
            payment.id, 
            PaymentStatus.COMPLETED,
            provider_transaction_id=verify_result.get("transaction_id"),
            provider_response=verify_result["provider_response"]
        )
        
        # Top up wallet if it's a wallet top-up
        if payment.payment_type == PaymentType.WALLET_TOPUP:
            wallet = await get_user_wallet_by_currency(db, payment.user_id, payment.currency)
            if wallet:
                await deposit(db, wallet.id, payment.amount, "Wallet top-up via payment gateway")
        
        return {"success": True, "message": "Payment verified successfully"}
    else:
        # Update payment status to failed
        await update_payment_status(db, payment.id, PaymentStatus.FAILED, verify_result["error"])
        raise HTTPException(status_code=400, detail=verify_result["error"])

# -----------------------------
# Get User Payments
# -----------------------------
@router.get("/user/payments", response_model=List[PaymentOut], operation_id="get_user_payments")
async def get_user_payments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: PaymentStatus = Query(None),
    payment_type: PaymentType = Query(None)
):
    """Get user's payment history"""
    payments = await list_user_payments(
        db, 
        current_user.id, 
        page=page, 
        page_size=page_size,
        status=status,
        payment_type=payment_type
    )
    return [PaymentOut.model_validate(payment) for payment in payments]

# -----------------------------
# Get Payment Details
# -----------------------------
@router.get("/{payment_id}", response_model=PaymentOut, operation_id="get_payment")
async def get_payment_details(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get payment details"""
    payment = await get_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this payment")
    
    return PaymentOut.model_validate(payment)

# -----------------------------
# Cancel Payment
# -----------------------------
@router.post("/{payment_id}/cancel", operation_id="cancel_payment")
async def cancel_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Cancel a pending payment"""
    payment = await get_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this payment")
    
    if payment.status != PaymentStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only pending payments can be cancelled")
    
    await update_payment_status(db, payment_id, PaymentStatus.CANCELLED)
    return {"success": True, "message": "Payment cancelled successfully"}

# -----------------------------
# Payment Statistics
# -----------------------------
@router.get("/user/statistics", operation_id="get_payment_statistics")
async def get_payment_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
    days: int = Query(30, ge=1, le=365)
):
    """Get user's payment statistics"""
    from datetime import timedelta
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get payment statistics
    result = await db.execute(
        select(Payment)
        .where(Payment.user_id == current_user.id)
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
            provider_stats[provider] = {"count": 0, "amount": 0}
        provider_stats[provider]["count"] += 1
        if payment.status == PaymentStatus.COMPLETED:
            provider_stats[provider]["amount"] += payment.amount
    
    return {
        "total_payments": total_payments,
        "total_amount": total_amount,
        "successful_payments": successful_payments,
        "failed_payments": failed_payments,
        "success_rate": (successful_payments / total_payments * 100) if total_payments > 0 else 0,
        "provider_statistics": provider_stats,
        "period_days": days
    }

# Helper functions
def get_provider_api_key(provider_name: str) -> str:
    """Get provider API key from environment variables"""
    env_var = f"{provider_name.upper()}_API_KEY"
    return os.getenv(env_var, "test_key")

def get_provider_merchant_id(provider_name: str) -> str:
    """Get provider merchant ID from environment variables"""
    env_var = f"{provider_name.upper()}_MERCHANT_ID"
    return os.getenv(env_var, "test_merchant")

import os
import logging
logger = logging.getLogger(__name__)

# -----------------------------
# Invoice PDF
# -----------------------------
@router.get("/{payment_id}/invoice.pdf")
async def get_payment_invoice_pdf(payment_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_session)):
    payment = await get_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this invoice")

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, "Invoice")
    y -= 30

    pdf.setFont("Helvetica", 10)
    fields = [
        ("Invoice ID", str(payment.id)),
        ("Date", payment.created_at.strftime("%Y-%m-%d %H:%M") if payment.created_at else ""),
        ("User ID", str(payment.user_id)),
        ("Amount", f"{payment.amount} {payment.currency}"),
        ("Status", str(payment.status)),
        ("Method", str(payment.payment_method)),
        ("Type", str(payment.payment_type)),
        ("Reference", payment.reference_id or ""),
        ("Description", payment.description or ""),
    ]
    for label, value in fields:
        pdf.drawString(50, y, f"{label}: {value}")
        y -= 18
        if y < 100:
            pdf.showPage(); y = height - 50

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return Response(buffer.getvalue(), media_type="application/pdf")
