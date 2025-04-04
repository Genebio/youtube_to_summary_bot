import json
from typing import Any, Optional, TypeVar, Callable, Awaitable
from functools import wraps
import redis.asyncio as redis
from utils.logger import logger
from config.config import REDIS_URL, CACHE_EXPIRY_SECONDS

# Create the Redis client
redis_client = redis.from_url(REDIS_URL) if REDIS_URL else None

# Type variable for function return type
T = TypeVar('T')


async def get_cached_data(key: str) -> Optional[Any]:
    """Retrieve data from the Redis cache by key."""
    if not redis_client:
        return None
    
    try:
        data = await redis_client.get(key)
        if data:
            logger.info(f"Cache hit for key: {key}")
            return json.loads(data)
        logger.info(f"Cache miss for key: {key}")
        return None
    except Exception as e:
        logger.error(f"Error retrieving data from cache: {str(e)}")
        return None


async def set_cached_data(key: str, data: Any, expiry: int = CACHE_EXPIRY_SECONDS) -> bool:
    """Store data in the Redis cache with the given key and expiry time."""
    if not redis_client:
        return False
    
    try:
        serialized_data = json.dumps(data)
        await redis_client.setex(key, expiry, serialized_data)
        logger.info(f"Data cached with key: {key}, expiry: {expiry}s")
        return True
    except Exception as e:
        logger.error(f"Error caching data: {str(e)}")
        return False


def cached(expiry: int = CACHE_EXPIRY_SECONDS) -> Callable:
    """Decorator to cache the result of an async function."""
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            if not redis_client:
                return await func(*args, **kwargs)
            
            # Create a cache key from the function name and arguments
            key_parts = [func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
            cache_key = ":".join(key_parts)
            
            # Try to get cached result
            cached_result = await get_cached_data(cache_key)
            if cached_result is not None:
                return cached_result
            
            # If not cached, call the function and cache the result
            result = await func(*args, **kwargs)
            if result:
                await set_cached_data(cache_key, result, expiry)
            return result
        
        return wrapper
    
    return decorator


async def clear_cache(pattern: str = "*") -> int:
    """Clear cache entries matching the given pattern."""
    if not redis_client:
        return 0
    
    try:
        keys = await redis_client.keys(pattern)
        if not keys:
            return 0
        
        count = await redis_client.delete(*keys)
        logger.info(f"Cleared {count} keys from cache matching pattern: {pattern}")
        return count
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        return 0


# Health check function for Redis
async def check_redis_connection() -> bool:
    """Check if Redis connection is working."""
    if not redis_client:
        logger.warning("Redis client not configured")
        return False
    
    try:
        await redis_client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis connection error: {str(e)}")
        return False