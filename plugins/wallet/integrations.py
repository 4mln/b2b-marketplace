from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from .crud import get_user_wallet_by_currency, withdraw, deposit, apply_cashback
from .models import TransactionType

# Integration functions for other plugins to use

async def process_marketplace_payment(db: AsyncSession, user_id: int, amount: float, currency: str, reference: str, description: str) -> bool:
    """Process a payment for marketplace features like posting inquiries or tenders.
    
    Args:
        db: Database session
        user_id: ID of the user making the payment
        amount: Amount to be paid
        currency: Currency code
        reference: Reference ID (e.g., inquiry ID, tender ID)
        description: Description of the payment
        
    Returns:
        bool: True if payment was successful, False otherwise
    """
    try:
        # Get user's wallet for the specified currency
        wallet = await get_user_wallet_by_currency(db, user_id, currency)
        if not wallet:
            return False
        
        # Check if user has sufficient funds
        if wallet.balance < amount:
            return False
        
        # Process the payment
        await withdraw(
            db,
            wallet.id,
            amount,
            reference=reference,
            description=description
        )
        
        return True
    except Exception:
        return False

async def process_marketplace_refund(db: AsyncSession, user_id: int, amount: float, currency: str, reference: str, description: str) -> bool:
    """Process a refund for marketplace features.
    
    Args:
        db: Database session
        user_id: ID of the user receiving the refund
        amount: Amount to be refunded
        currency: Currency code
        reference: Reference ID (e.g., inquiry ID, tender ID)
        description: Description of the refund
        
    Returns:
        bool: True if refund was successful, False otherwise
    """
    try:
        # Get user's wallet for the specified currency
        wallet = await get_user_wallet_by_currency(db, user_id, currency)
        if not wallet:
            return False
        
        # Process the refund
        await deposit(
            db,
            wallet.id,
            amount,
            reference=reference,
            description=description
        )
        
        return True
    except Exception:
        return False

async def process_marketplace_cashback(db: AsyncSession, user_id: int, amount: float, percentage: float, currency: str, reference: str) -> bool:
    """Process cashback for marketplace transactions.
    
    Args:
        db: Database session
        user_id: ID of the user receiving the cashback
        amount: Original transaction amount
        percentage: Cashback percentage
        currency: Currency code
        reference: Reference ID (e.g., order ID)
        
    Returns:
        bool: True if cashback was successful, False otherwise
    """
    try:
        # Get user's wallet for the specified currency
        wallet = await get_user_wallet_by_currency(db, user_id, currency)
        if not wallet:
            return False
        
        # Process the cashback
        await apply_cashback(
            db,
            wallet.id,
            amount,
            percentage,
            reference=reference
        )
        
        return True
    except Exception:
        return False

async def check_user_balance(db: AsyncSession, user_id: int, currency: str) -> Optional[float]:
    """Check a user's balance for a specific currency.
    
    Args:
        db: Database session
        user_id: ID of the user
        currency: Currency code
        
    Returns:
        Optional[float]: User's balance if wallet exists, None otherwise
    """
    wallet = await get_user_wallet_by_currency(db, user_id, currency)
    if not wallet:
        return None
    
    return wallet.balance

async def has_sufficient_funds(db: AsyncSession, user_id: int, amount: float, currency: str) -> bool:
    """Check if a user has sufficient funds for a transaction.
    
    Args:
        db: Database session
        user_id: ID of the user
        amount: Amount to check
        currency: Currency code
        
    Returns:
        bool: True if user has sufficient funds, False otherwise
    """
    balance = await check_user_balance(db, user_id, currency)
    if balance is None:
        return False
    
    return balance >= amount