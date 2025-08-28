from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from plugins.auth.models import User
from plugins.wallet.integrations import process_marketplace_payment, has_sufficient_funds

async def handle_inquiry_payment(db: AsyncSession, user: User, inquiry_id: int, amount: float, currency: str = "USD") -> bool:
    """Handle payment for posting an inquiry.
    
    Args:
        db: Database session
        user: Current user
        inquiry_id: ID of the inquiry being posted
        amount: Payment amount
        currency: Currency code (default: USD)
        
    Returns:
        bool: True if payment was successful
        
    Raises:
        HTTPException: If payment fails
    """
    # Check if user has sufficient funds
    has_funds = await has_sufficient_funds(db, user.id, amount, currency)
    if not has_funds:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient funds in your wallet"
        )
    
    # Process the payment
    payment_success = await process_marketplace_payment(
        db,
        user.id,
        amount,
        currency,
        reference=f"inquiry_{inquiry_id}",
        description=f"Payment for posting inquiry #{inquiry_id}"
    )
    
    if not payment_success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment processing failed"
        )
    
    return True

async def handle_tender_payment(db: AsyncSession, user: User, tender_id: int, amount: float, currency: str = "USD") -> bool:
    """Handle payment for posting a tender.
    
    Args:
        db: Database session
        user: Current user
        tender_id: ID of the tender being posted
        amount: Payment amount
        currency: Currency code (default: USD)
        
    Returns:
        bool: True if payment was successful
        
    Raises:
        HTTPException: If payment fails
    """
    # Check if user has sufficient funds
    has_funds = await has_sufficient_funds(db, user.id, amount, currency)
    if not has_funds:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient funds in your wallet"
        )
    
    # Process the payment
    payment_success = await process_marketplace_payment(
        db,
        user.id,
        amount,
        currency,
        reference=f"tender_{tender_id}",
        description=f"Payment for posting tender #{tender_id}"
    )
    
    if not payment_success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment processing failed"
        )
    
    return True

# Example usage in a route

"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from plugins.auth.models import User
from .inquiry_payment import handle_inquiry_payment
from .schemas import InquiryCreate, InquiryOut

router = APIRouter()

@router.post("/inquiries/", response_model=InquiryOut)
async def create_inquiry(
    inquiry: InquiryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Handle payment first
    await handle_inquiry_payment(
        db,
        current_user,
        inquiry_id=0,  # Temporary ID, will be updated after creation
        amount=10.0,  # Fixed price for posting an inquiry
    )
    
    # Create the inquiry
    db_inquiry = await create_inquiry_in_db(db, inquiry, current_user.id)
    
    # Update the payment reference with the actual inquiry ID
    # This would require additional code to update the transaction reference
    
    return db_inquiry
"""