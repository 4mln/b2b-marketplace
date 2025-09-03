from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from plugins.pricing.schemas import Price, PriceResponse

router = APIRouter()

# -----------------------------
# Health check
# -----------------------------
@router.get("/health", summary="Health check for pricing plugin")
async def health():
    return {"ok": True, "plugin": "pricing"}

# -----------------------------
# Fetch product pricing
# -----------------------------
@router.get("/{product_id}", response_model=PriceResponse, summary="Get product pricing")
async def get_product_price(
    product_id: int,
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session),
    include_discounts: bool = Query(True, description="Include discount calculations")
):
    """
    Fetch the pricing info for a product. Discounts applied if enabled.
    """
    # Placeholder: Replace with actual DB query
    base_price = 100.0  # Example
    discount = 0.0

    if include_discounts:
        discount = 10.0  # Example discount, replace with dynamic calculation

    final_price = base_price - discount

    price_data = Price(
        product_id=product_id,
        base_price=base_price,
        discount=discount,
        final_price=final_price,
        currency="USD"
    )

    return PriceResponse(prices=[price_data])