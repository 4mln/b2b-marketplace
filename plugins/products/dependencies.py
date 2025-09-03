# plugins/products/dependencies.py
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from plugins.subscriptions.crud import check_plan_limits
from plugins.products.models import Product

async def enforce_product_limit(user_id: int, db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    """Ensure the seller/buyer does not exceed subscription product limit."""
    plan = await check_plan_limits(user_id, db)
    if not plan:
        raise HTTPException(status_code=403, detail="No active subscription")

    # Count products for seller
    result = await db.execute(
        select(func.count()).select_from(Product).where(Product.seller_id == user_id)
    )
    count = result.scalar_one()

    if plan.max_products is not None and count >= plan.max_products:
        raise HTTPException(
            status_code=403,
            detail=f"Product limit reached for your subscription ({plan.max_products})"
        )