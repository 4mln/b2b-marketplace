from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
import numpy as np

from plugins.wallet.integrations import check_user_balance

async def get_personalized_recommendations(db: AsyncSession, user_id: int, product_embeddings: Dict[int, np.ndarray], top_n: int = 5) -> List[Dict[str, Any]]:
    """Get personalized product recommendations for a user based on their wallet balance and product embeddings.
    
    This function demonstrates how the wallet plugin can be integrated with AI features.
    It uses the user's wallet balance as a factor in the recommendation algorithm.
    
    Args:
        db: Database session
        user_id: ID of the user
        product_embeddings: Dictionary mapping product IDs to their vector embeddings
        top_n: Number of recommendations to return
        
    Returns:
        List[Dict[str, Any]]: List of recommended products with scores
    """
    # Get user's wallet balance (USD as default currency)
    balance = await check_user_balance(db, user_id, "USD")
    
    # Default balance if user has no wallet
    if balance is None:
        balance = 0.0
    
    # Get user preferences (this would come from a user embeddings table in a real implementation)
    # For this example, we'll create a mock user embedding
    user_embedding = np.random.rand(384)  # Assuming 384-dimensional embeddings
    
    # Calculate similarity scores between user and products
    recommendations = []
    for product_id, embedding in product_embeddings.items():
        # Calculate cosine similarity
        similarity = np.dot(user_embedding, embedding) / (np.linalg.norm(user_embedding) * np.linalg.norm(embedding))
        
        # Adjust recommendation score based on wallet balance
        # Products that are within the user's budget get a boost
        # This is a simplified example - in a real system, you would have product prices
        product_price = 100.0  # Mock price, would come from product database
        
        # Boost score if user can afford the product
        affordability_boost = 1.0 if balance >= product_price else 0.8
        
        # Final recommendation score
        final_score = similarity * affordability_boost
        
        recommendations.append({
            "product_id": product_id,
            "similarity_score": float(similarity),
            "affordability_boost": affordability_boost,
            "final_score": float(final_score)
        })
    
    # Sort by final score and return top N
    recommendations.sort(key=lambda x: x["final_score"], reverse=True)
    return recommendations[:top_n]

async def get_price_recommendations(db: AsyncSession, user_id: int, product_id: int) -> Dict[str, Any]:
    """Get price recommendations for a product based on user's wallet balance and market data.
    
    This function demonstrates how the wallet plugin can be integrated with AI pricing features.
    
    Args:
        db: Database session
        user_id: ID of the user
        product_id: ID of the product
        
    Returns:
        Dict[str, Any]: Price recommendations
    """
    # Get user's wallet balances for different currencies
    usd_balance = await check_user_balance(db, user_id, "USD") or 0.0
    eur_balance = await check_user_balance(db, user_id, "EUR") or 0.0
    
    # In a real implementation, you would get historical price data and use ML models
    # For this example, we'll create mock data
    
    # Mock market price range
    market_min_price = 80.0
    market_max_price = 120.0
    market_avg_price = 100.0
    
    # Calculate recommended price based on market data and user's wallet balance
    # If user has high balance, recommend higher price point
    # If user has low balance, recommend lower price point
    
    # Normalize user balance to a factor between 0.8 and 1.2
    balance_factor = 1.0
    if usd_balance > 0:
        balance_factor = min(1.2, max(0.8, (usd_balance / 1000) + 0.8))
    
    recommended_price = market_avg_price * balance_factor
    
    # Ensure price is within market range
    recommended_price = min(market_max_price, max(market_min_price, recommended_price))
    
    return {
        "product_id": product_id,
        "market_min_price": market_min_price,
        "market_max_price": market_max_price,
        "market_avg_price": market_avg_price,
        "recommended_price": recommended_price,
        "user_balance_factor": balance_factor,
        "available_currencies": {
            "USD": usd_balance,
            "EUR": eur_balance
        }
    }