from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional


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
from plugins.products.dependencies import enforce_product_limit
from app.core.openapi import enhance_endpoint_docs
from plugins.products.docs import product_docs
from plugins.search.routes import sync_products as search_sync_products  # reuse sync

router = APIRouter()
# -----------------------------
# Public Product List (no seller identity)
# -----------------------------
@router.get("/public", response_model=List[ProductOut], operation_id="product_public_list")
async def public_products_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Results per page"),
    sort_by: str = Query("id", description="Field to sort by"),
    sort_dir: str = Query("asc", regex="^(asc|desc)$", description="Sort direction"),
    search: Optional[str] = Query(None, description="Search term for product name"),
    guild_id: Optional[int] = Query(None, description="Filter by guild id"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    city: Optional[str] = Query(None, description="Filter by city"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    boosted: bool = Query(False, description="Apply subscription-based boosts"),
    synonyms: Optional[List[str]] = Query(None, description="Synonyms for search"),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session),
) -> List[ProductOut]:
    """Public catalog: hides seller identity at response layer (schema does not include seller)."""
    items = await list_products(
        db,
        page,
        page_size,
        sort_by,
        sort_dir,
        search,
        guild_id,
        min_price,
        max_price,
        city,
        brand,
        boosted,
        synonyms,
    )
    # filter only approved for public
    return [p for p in items if getattr(p, "status", "approved") == "approved"]


# -----------------------------
# Discovery sections placeholders
# -----------------------------
@router.get("/sections/recommended", response_model=List[ProductOut], operation_id="product_recommended")
async def recommended_products(db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    return await list_products(db, page=1, page_size=10, sort_by="id", sort_dir="desc")


@router.get("/sections/trending", response_model=List[ProductOut], operation_id="product_trending")
async def trending_products(db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    return await list_products(db, page=1, page_size=10, sort_by="id", sort_dir="desc")


@router.get("/sections/new", response_model=List[ProductOut], operation_id="product_new")
async def new_products(db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)):
    return await list_products(db, page=1, page_size=10, sort_by="created_at", sort_dir="desc")

# -----------------------------
# Create Product
# -----------------------------
@router.post("/", response_model=ProductOut, operation_id="product_create")
async def create_product_endpoint(
    product: ProductCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session),
    _: None = Depends(enforce_product_limit), # ✅ enforce product limit
) -> ProductOut:
    """Create a new product linked to the current user (seller)."""
    created = await create_product(db, product, user.id)
    # trigger async search index sync (best-effort)
    try:
        await search_sync_products(db)
    except Exception:
        pass
    return created

# -----------------------------
# Get Product by ID
# -----------------------------
@router.get("/{product_id}", response_model=ProductOut, operation_id="product_get_by_id")
async def get_product_endpoint(
    product_id: int,
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session),
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
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session),
) -> ProductOut:
    """Update an existing product (only owner can update)."""
    db_product = await update_product(db, product_id, product_data, user.id)
    if not db_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found or permission denied",
        )
    # trigger async search index sync (best-effort)
    try:
        await search_sync_products(db)
    except Exception:
        pass
    return db_product

# -----------------------------
# Delete Product
# -----------------------------
@router.delete("/{product_id}", response_model=dict, operation_id="product_delete")
async def delete_product_endpoint(
    product_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session),
) -> dict:
    """Delete an existing product (only owner can delete)."""
    success = await delete_product(db, product_id, user.id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Product not found or permission denied",
        )
    # trigger async search index sync (best-effort)
    try:
        await search_sync_products(db)
    except Exception:
        pass
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
    guild_id: Optional[int] = Query(None, description="Filter by guild id"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    city: Optional[str] = Query(None, description="Filter by city"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    boosted: bool = Query(False, description="Apply subscription-based boosts"),
    synonyms: Optional[List[str]] = Query(None, description="Synonyms for search"),
    db: AsyncSession = Depends(lambda: __import__("importlib").import_module("app.db.session").get_session),
) -> List[ProductOut]:
    """List all products with pagination, sorting, and filters."""
    return await list_products(
        db,
        page,
        page_size,
        sort_by,
        sort_dir,
        search,
        guild_id,
        min_price,
        max_price,
        city,
        brand,
        boosted,
        synonyms,
    )


# Apply OpenAPI documentation enhancements
enhance_endpoint_docs(router, product_docs)