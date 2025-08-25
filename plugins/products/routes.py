from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.db import get_session
from plugins.products.schemas import ProductCreate, ProductUpdate, ProductOut
from plugins.products.crud import (
    create_product,
    get_product,
    update_product,
    delete_product,
    list_products,
)
from plugins.user.security import get_current_user
from plugins.user.models import User

router = APIRouter()

# -----------------------------
# Create Product
# -----------------------------
@router.post("/", response_model=ProductOut, operation_id="product_create")
async def create_product_endpoint(
    product: ProductCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> ProductOut:
    """Create a new product linked to the current user (seller)."""
    return await create_product(db, product, user.id)

# -----------------------------
# Get Product by ID
# -----------------------------
@router.get("/{product_id}", response_model=ProductOut, operation_id="product_get_by_id")
async def get_product_endpoint(
    product_id: int,
    db: AsyncSession = Depends(get_session),
) -> ProductOut:
    """Fetch a product by its ID."""
    db_product = await get_product(db, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

# -----------------------------
# Update Product
# -----------------------------
@router.put("/{product_id}", response_model=ProductOut, operation_id="product_update")
async def update_product_endpoint(
    product_id: int,
    product_data: ProductUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> ProductOut:
    """Update an existing product (only owner can update)."""
    db_product = await update_product(db, product_id, product_data, user.id)
    if not db_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found or permission denied",
        )
    return db_product

# -----------------------------
# Delete Product
# -----------------------------
@router.delete("/{product_id}", response_model=dict, operation_id="product_delete")
async def delete_product_endpoint(
    product_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> dict:
    """Delete an existing product (only owner can delete)."""
    success = await delete_product(db, product_id, user.id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Product not found or permission denied",
        )
    return {"detail": "Product deleted successfully"}

# -----------------------------
# List / Search Products
# -----------------------------
@router.get("/", response_model=List[ProductOut], operation_id="product_list")
async def list_products_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Results per page"),
    sort_by: str = Query("id", description="Field to sort by"),
    sort_dir: str = Query("asc", regex="^(asc|desc)$", description="Sort direction"),
    search: Optional[str] = Query(None, description="Search term for product name"),
    db: AsyncSession = Depends(get_session),
) -> List[ProductOut]:
    """List all products with pagination, sorting, and filters."""
    return await list_products(db, page, page_size, sort_by, sort_dir, search)