from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from typing import List, Dict, Any
from .models import Seller
from .schemas import SellerCreate, SellerUpdate, StorePolicyUpdate, StoreAnalytics

# -----------------------------
# Seller CRUD
# -----------------------------
async def create_seller(db: AsyncSession, seller_data: SellerCreate, user_id: int) -> Seller:
    new_seller = Seller(**seller_data.dict(), user_id=user_id)
    db.add(new_seller)
    await db.commit()
    await db.refresh(new_seller)
    return new_seller

async def get_seller(db: AsyncSession, seller_id: int) -> Seller | None:
    return await db.get(Seller, seller_id)

async def get_seller_by_user_id(db: AsyncSession, user_id: int) -> Seller | None:
    result = await db.execute(select(Seller).where(Seller.user_id == user_id))
    return result.scalars().first()

async def update_seller(db: AsyncSession, seller_id: int, seller_data: SellerUpdate, user_id: int) -> Seller | None:
    seller = await db.get(Seller, seller_id)
    if seller and seller.user_id == user_id:
        for key, value in seller_data.dict(exclude_unset=True).items():
            setattr(seller, key, value)
        seller.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(seller)
        return seller
    return None

async def delete_seller(db: AsyncSession, seller_id: int, user_id: int) -> bool:
    seller = await db.get(Seller, seller_id)
    if seller and seller.user_id == user_id:
        await db.delete(seller)
        await db.commit()
        return True
    return False

async def list_sellers(db: AsyncSession, offset: int = 0, limit: int = 10, search: str = None, subscription_type: str = None):
    query = select(Seller)
    
    if search:
        query = query.where(Seller.name.ilike(f"%{search}%"))
    
    if subscription_type:
        query = query.where(Seller.subscription == subscription_type)
    
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

# -----------------------------
# Store Policies
# -----------------------------
async def update_store_policies(db: AsyncSession, seller_id: int, policies: StorePolicyUpdate) -> Seller:
    seller = await db.get(Seller, seller_id)
    if not seller:
        raise ValueError("Seller not found")
    
    # Update store policies
    current_policies = seller.store_policies or {}
    updated_policies = {**current_policies, **policies.dict(exclude_unset=True)}
    
    seller.store_policies = updated_policies
    seller.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(seller)
    return seller

# -----------------------------
# Store Analytics
# -----------------------------
async def get_store_analytics(db: AsyncSession, seller_id: int, days: int = 30) -> StoreAnalytics:
    """Get comprehensive store analytics for a seller"""
    from plugins.products.models import Product
    from plugins.orders.models import Order
    from plugins.ratings.models import Rating
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get total products
    total_products_result = await db.execute(
        select(func.count(Product.id))
        .where(Product.seller_id == seller_id)
        .where(Product.status == "approved")
    )
    total_products = total_products_result.scalar() or 0
    
    # Get total orders and revenue
    orders_result = await db.execute(
        select(func.count(Order.id), func.sum(Order.total_amount))
        .where(Order.seller_id == seller_id)
        .where(Order.created_at >= start_date)
    )
    total_orders, total_revenue = orders_result.first()
    total_orders = total_orders or 0
    total_revenue = total_revenue or 0.0
    
    # Get average rating
    ratings_result = await db.execute(
        select(func.avg((Rating.quality + Rating.timeliness + Rating.communication + Rating.reliability) / 4))
        .where(Rating.ratee_id == seller_id)
    )
    average_rating = ratings_result.scalar() or 0.0
    
    # Get total ratings count
    total_ratings_result = await db.execute(
        select(func.count(Rating.id))
        .where(Rating.ratee_id == seller_id)
    )
    total_ratings = total_ratings_result.scalar() or 0
    
    # Mock analytics data (in real implementation, these would come from analytics service)
    store_visits = 1500  # Mock data
    unique_visitors = 800  # Mock data
    conversion_rate = (total_orders / store_visits * 100) if store_visits > 0 else 0
    
    # Get top products (mock data for now)
    top_products = [
        {"id": 1, "name": "Product A", "sales": 150, "revenue": 15000.0},
        {"id": 2, "name": "Product B", "sales": 120, "revenue": 12000.0},
        {"id": 3, "name": "Product C", "sales": 100, "revenue": 10000.0},
    ]
    
    # Get recent orders (mock data for now)
    recent_orders = [
        {"id": 1, "total": 5000.0, "status": "completed", "created_at": "2024-01-15"},
        {"id": 2, "total": 3000.0, "status": "pending", "created_at": "2024-01-14"},
        {"id": 3, "total": 7500.0, "status": "completed", "created_at": "2024-01-13"},
    ]
    
    # Generate revenue trend (mock data)
    revenue_trend = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        revenue_trend.append({
            "date": date.strftime("%Y-%m-%d"),
            "revenue": 1000 + (i * 50)  # Mock increasing trend
        })
    
    # Generate visitor trend (mock data)
    visitor_trend = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        visitor_trend.append({
            "date": date.strftime("%Y-%m-%d"),
            "visitors": 50 + (i * 2)  # Mock increasing trend
        })
    
    return StoreAnalytics(
        total_products=total_products,
        total_orders=total_orders,
        total_revenue=total_revenue,
        average_rating=round(average_rating, 2),
        total_ratings=total_ratings,
        store_visits=store_visits,
        unique_visitors=unique_visitors,
        conversion_rate=round(conversion_rate, 2),
        top_products=top_products,
        recent_orders=recent_orders,
        revenue_trend=revenue_trend,
        visitor_trend=visitor_trend
    )

# -----------------------------
# Featured Sellers
# -----------------------------
async def get_featured_sellers(db: AsyncSession, limit: int = 10) -> List[Seller]:
    """Get featured sellers for homepage"""
    result = await db.execute(
        select(Seller)
        .where(Seller.is_featured == True)
        .where(Seller.is_verified == True)
        .limit(limit)
    )
    return result.scalars().all()

# -----------------------------
# Search Sellers
# -----------------------------
async def search_sellers(
    db: AsyncSession, 
    query: str = None, 
    industry: str = None, 
    location: str = None,
    verified_only: bool = False,
    offset: int = 0, 
    limit: int = 10
) -> List[Seller]:
    """Advanced seller search with filters"""
    from plugins.auth.models import User
    
    # Start with base query
    base_query = select(Seller).join(User, Seller.user_id == User.id)
    
    # Apply filters
    if query:
        base_query = base_query.where(
            Seller.name.ilike(f"%{query}%") | 
            User.business_name.ilike(f"%{query}%") |
            User.business_industry.ilike(f"%{query}%")
        )
    
    if industry:
        base_query = base_query.where(User.business_industry.ilike(f"%{industry}%"))
    
    if location:
        # Search in business addresses
        base_query = base_query.where(User.business_addresses.contains([{"city": location}]))
    
    if verified_only:
        base_query = base_query.where(Seller.is_verified == True)
    
    # Apply pagination
    base_query = base_query.offset(offset).limit(limit)
    
    result = await db.execute(base_query)
    return result.scalars().all()

# -----------------------------
# Seller Statistics
# -----------------------------
async def get_seller_statistics(db: AsyncSession, seller_id: int) -> Dict[str, Any]:
    """Get comprehensive seller statistics"""
    from plugins.products.models import Product
    from plugins.orders.models import Order
    from plugins.ratings.models import Rating
    
    # Get seller
    seller = await get_seller(db, seller_id)
    if not seller:
        return {}
    
    # Get product statistics
    products_result = await db.execute(
        select(func.count(Product.id))
        .where(Product.seller_id == seller_id)
    )
    total_products = products_result.scalar() or 0
    
    approved_products_result = await db.execute(
        select(func.count(Product.id))
        .where(Product.seller_id == seller_id)
        .where(Product.status == "approved")
    )
    approved_products = approved_products_result.scalar() or 0
    
    # Get order statistics
    orders_result = await db.execute(
        select(func.count(Order.id), func.sum(Order.total_amount))
        .where(Order.seller_id == seller_id)
    )
    total_orders, total_revenue = orders_result.first()
    total_orders = total_orders or 0
    total_revenue = total_revenue or 0.0
    
    # Get rating statistics
    ratings_result = await db.execute(
        select(
            func.count(Rating.id),
            func.avg((Rating.quality + Rating.timeliness + Rating.communication + Rating.reliability) / 4)
        )
        .where(Rating.ratee_id == seller_id)
    )
    total_ratings, avg_rating = ratings_result.first()
    total_ratings = total_ratings or 0
    avg_rating = avg_rating or 0.0
    
    return {
        "seller_id": seller_id,
        "total_products": total_products,
        "approved_products": approved_products,
        "pending_products": total_products - approved_products,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "total_ratings": total_ratings,
        "average_rating": round(avg_rating, 2),
        "is_verified": seller.is_verified,
        "is_featured": seller.is_featured,
        "subscription": seller.subscription,
        "created_at": seller.created_at,
        "updated_at": seller.updated_at
    }
