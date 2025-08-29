from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional

from plugins.products.models import Product
from plugins.products.schemas import ProductCreate, ProductUpdate

# -----------------------------
# Create Product
# -----------------------------
async def create_product(db: AsyncSession, product: ProductCreate, seller_id: int) -> Product:
    db_product = Product(**product.dict(), seller_id=seller_id)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

# -----------------------------
# Get Product by ID
# -----------------------------
async def get_product(db: AsyncSession, product_id: int) -> Optional[Product]:
    return await db.get(Product, product_id)

# -----------------------------
# Update Product
# -----------------------------
async def update_product(db: AsyncSession, product_id: int, product_data: ProductUpdate, seller_id: int) -> Optional[Product]:
    db_product = await db.get(Product, product_id)
    if not db_product or db_product.seller_id != seller_id:
        return None
    for key, value in product_data.dict(exclude_unset=True).items():
        setattr(db_product, key, value)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

# -----------------------------
# Delete Product
# -----------------------------
async def delete_product(db: AsyncSession, product_id: int, seller_id: int) -> bool:
    db_product = await db.get(Product, product_id)
    if not db_product or db_product.seller_id != seller_id:
        return False
    await db.delete(db_product)
    await db.commit()
    return True

# -----------------------------
# List / Search Products
# -----------------------------
async def list_products(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "id",
    sort_dir: str = "asc",
    search: Optional[str] = None,
    guild_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    city: Optional[str] = None,
    brand: Optional[str] = None,
    apply_boosts: bool = False,
    synonyms: Optional[list[str]] = None,
) -> List[Product]:
    query = select(Product)
    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))
    # naive synonyms: OR search terms
    if synonyms:
        for syn in synonyms:
            query = query.where(Product.name.ilike(f"%{syn}%"))
    if guild_id is not None:
        query = query.where(Product.guild_id == guild_id)
    if min_price is not None:
        query = query.where(Product.price >= min_price)
    if max_price is not None:
        query = query.where(Product.price <= max_price)
    # city and brand stored in custom_metadata JSON (if present)
    if city is not None:
        query = query.where(Product.custom_metadata["city"].as_string() == city)
    if brand is not None:
        query = query.where(Product.custom_metadata["brand"].as_string() == brand)
    if apply_boosts and sort_by in ("id", "created_at"):
        # Placeholder: prioritize newer products when boosted
        query = query.order_by(getattr(Product, "created_at").desc())
    else:
        if sort_dir.lower() == "desc":
            query = query.order_by(getattr(Product, sort_by).desc())
        else:
            query = query.order_by(getattr(Product, sort_by).asc())
    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    return result.scalars().all()