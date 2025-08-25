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
    search: Optional[str] = None
) -> List[Product]:
    query = select(Product)
    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))
    if sort_dir.lower() == "desc":
        query = query.order_by(getattr(Product, sort_by).desc())
    else:
        query = query.order_by(getattr(Product, sort_by).asc())
    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    return result.scalars().all()