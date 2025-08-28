from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List

from app.core.deps import get_db, get_current_user
from plugins.auth.models import User
from plugins.wallet.integrations import process_marketplace_payment, process_marketplace_cashback, has_sufficient_funds

async def process_order_payment(db: AsyncSession, user: User, order_id: int, total_amount: float, currency: str = "USD", cashback_percentage: float = 1.0) -> Dict[str, Any]:
    """Process payment for an order in the marketplace.
    
    Args:
        db: Database session
        user: Current user making the purchase
        order_id: ID of the order
        total_amount: Total order amount
        currency: Currency code (default: USD)
        cashback_percentage: Cashback percentage to apply (default: 1.0%)
        
    Returns:
        Dict[str, Any]: Payment result with transaction details
        
    Raises:
        HTTPException: If payment fails
    """
    # Check if user has sufficient funds
    has_funds = await has_sufficient_funds(db, user.id, total_amount, currency)
    if not has_funds:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient funds in your wallet"
        )
    
    # Process the payment
    payment_success = await process_marketplace_payment(
        db,
        user.id,
        total_amount,
        currency,
        reference=f"order_{order_id}",
        description=f"Payment for order #{order_id}"
    )
    
    if not payment_success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment processing failed"
        )
    
    # Apply cashback if applicable
    cashback_success = False
    if cashback_percentage > 0:
        cashback_success = await process_marketplace_cashback(
            db,
            user.id,
            total_amount,
            cashback_percentage,
            currency,
            reference=f"order_{order_id}_cashback"
        )
    
    return {
        "order_id": order_id,
        "payment_status": "completed",
        "amount": total_amount,
        "currency": currency,
        "cashback_applied": cashback_success,
        "cashback_percentage": cashback_percentage,
        "cashback_amount": total_amount * (cashback_percentage / 100) if cashback_success else 0
    }

async def calculate_order_total(products: List[Dict[str, Any]], user_id: int, db: AsyncSession) -> Dict[str, Any]:
    """Calculate order total with potential discounts based on user's wallet balance.
    
    Args:
        products: List of products in the order with quantities
        user_id: ID of the user making the purchase
        db: Database session
        
    Returns:
        Dict[str, Any]: Order total calculation
    """
    from plugins.wallet.integrations import check_user_balance
    
    # Calculate base total
    subtotal = sum(product["price"] * product["quantity"] for product in products)
    
    # Check user's wallet balance
    balance = await check_user_balance(db, user_id, "USD") or 0.0
    
    # Apply loyalty discount based on wallet balance
    # This is a simple example - in a real system, you might have more complex logic
    discount_percentage = 0.0
    if balance >= 1000:
        discount_percentage = 5.0  # 5% discount for users with high balance
    elif balance >= 500:
        discount_percentage = 2.5  # 2.5% discount for users with medium balance
    
    discount_amount = subtotal * (discount_percentage / 100)
    total = subtotal - discount_amount
    
    # Calculate cashback percentage based on order total
    cashback_percentage = 1.0  # Default 1%
    if total >= 500:
        cashback_percentage = 3.0  # 3% cashback for large orders
    elif total >= 200:
        cashback_percentage = 2.0  # 2% cashback for medium orders
    
    return {
        "subtotal": subtotal,
        "discount_percentage": discount_percentage,
        "discount_amount": discount_amount,
        "total": total,
        "cashback_percentage": cashback_percentage,
        "estimated_cashback": total * (cashback_percentage / 100),
        "currency": "USD"
    }

# Example usage in a route

"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from plugins.auth.models import User
from .storefront_integration import process_order_payment, calculate_order_total
from .schemas import OrderCreate, OrderOut

router = APIRouter()

@router.post("/orders/", response_model=OrderOut)
async def create_order(
    order: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Calculate order total with potential discounts
    order_calculation = await calculate_order_total(order.products, current_user.id, db)
    
    # Create the order in database
    db_order = await create_order_in_db(db, order, current_user.id, order_calculation)
    
    # Process payment
    payment_result = await process_order_payment(
        db,
        current_user,
        db_order.id,
        order_calculation["total"],
        currency=order_calculation["currency"],
        cashback_percentage=order_calculation["cashback_percentage"]
    )
    
    # Update order with payment information
    db_order.payment_status = "paid"
    await db.commit()
    
    return db_order
"""