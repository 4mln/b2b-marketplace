# plugins/cart/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from .crud import create_cart, get_cart_by_user, add_item_to_cart, remove_item_from_cart
from .schemas import CartCreate, CartOut, CartItemCreate, CartItemOut

router = APIRouter(prefix="/cart", tags=["Cart"])

# Create new cart
@router.post("/", response_model=CartOut)
async def create_new_cart(cart_data: CartCreate, db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    cart = await create_cart(db, cart_data)
    return cart

# Get active cart by user
@router.get("/{user_id}", response_model=CartOut)
async def get_user_cart(user_id: int, db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    cart = await get_cart_by_user(db, user_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart

# Add item to cart
@router.post("/{cart_id}/items", response_model=CartItemOut)
async def add_cart_item(cart_id: int, item: CartItemCreate, db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    return await add_item_to_cart(db, cart_id, item)

# Remove item from cart
@router.delete("/items/{item_id}", response_model=dict)
async def remove_cart_item(item_id: int, db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    await remove_item_from_cart(db, item_id)
    return {"status": "ok", "deleted_item_id": item_id}
