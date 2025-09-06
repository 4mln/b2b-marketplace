from redis.asyncio import Redis
import asyncio

async def check_keys():
    redis = Redis.from_url('redis://redis:6379/0')
    keys = await redis.keys('api_key:*')
    print(f'API Keys: {keys}')
    await redis.close()

if __name__ == '__main__':
    asyncio.run(check_keys())