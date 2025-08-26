# plugins/cart/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from .models import Cart, CartItem
from .schemas import CartCreate, CartItemCreate

# Create a new cart
async def create_cart(db: AsyncSession, cart_data: CartCreate) -> Cart:
    cart = Cart(user_id=cart_data.user_id)
    db.add(cart)
    await db.flush()

    # Add items
    for item in cart_data.items:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.add(cart_item)

    await db.commit()
    await db.refresh(cart)
    return cart

# Get cart by user
async def get_cart_by_user(db: AsyncSession, user_id: int) -> Cart | None:
    result = await db.execute(select(Cart).where(Cart.user_id == user_id, Cart.is_active == True))
    return result.scalars().first()

# Add item to cart
async def add_item_to_cart(db: AsyncSession, cart_id: int, item: CartItemCreate) -> CartItem:
    cart_item = CartItem(cart_id=cart_id, product_id=item.product_id, quantity=item.quantity)
    db.add(cart_item)
    await db.commit()
    await db.refresh(cart_item)
    return cart_item

# Remove item from cart
async def remove_item_from_cart(db: AsyncSession, cart_item_id: int):
    item = await db.get(CartItem, cart_item_id)
    if item:
        await db.delete(item)
        await db.commit()
