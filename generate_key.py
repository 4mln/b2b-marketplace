from redis.asyncio import Redis
import asyncio
import json
from datetime import datetime, timedelta
import secrets

async def generate_api_key():
    redis = Redis.from_url('redis://redis:6379/0')
    
    # Generate a random API key
    api_key = secrets.token_urlsafe(32)
    
    # Create key info
    key_info = {
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "type": "test",
        "permissions": ["read", "write"]
    }
    
    # Store in Redis
    await redis.set(f"api_key:{api_key}", json.dumps(key_info))
    
    print(f'Generated API Key: {api_key}')
    print(f'Key Info: {key_info}')
    
    await redis.aclose()

if __name__ == '__main__':
    asyncio.run(generate_api_key())