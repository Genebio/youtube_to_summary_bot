from typing import Callable, Dict, Optional
from telegram import Update
from slowapi import Limiter
from slowapi.util import get_remote_address
from config.config import RATE_LIMIT_REQUESTS, RATE_LIMIT_PERIOD
from utils.logger import logger

# Create a rate limiter instance
limiter = Limiter(key_func=get_remote_address)

# Create a dictionary to store rate limit status for each user
user_rate_limits: Dict[str, bool] = {}


def rate_limited(
    limit: Optional[str] = None
) -> Callable:
    """
    Decorator for Telegram handlers to implement rate limiting.
    
    Args:
        limit: Rate limit string (e.g., "5/minute"). If not provided, uses the default from config.
        
    Returns:
        A decorator that can be applied to a Telegram handler function.
    """
    if limit is None:
        limit = f"{RATE_LIMIT_REQUESTS}/{RATE_LIMIT_PERIOD}s"
    
    def decorator(handler_func: Callable) -> Callable:
        async def wrapper(update: Update, context):
            # Get the Telegram user ID as the rate limit key
            user_id = str(update.effective_user.id)
            
            # Use a unique key for each user
            key = f"telegram:{user_id}"
            
            try:
                # Check if the user is already rate-limited
                if user_rate_limits.get(key, False):
                    logger.warning(f"User {user_id} is rate limited")
                    await update.message.reply_text(
                        "⚠️ You've reached the rate limit. Please try again later."
                    )
                    return
                
                # Check the rate limit
                if not limiter.check(key, limit):
                    logger.warning(f"Rate limit exceeded for user {user_id}")
                    user_rate_limits[key] = True
                    await update.message.reply_text(
                        "⚠️ You've reached the rate limit. Please try again later."
                    )
                    return
                
                # If not rate limited, update the counter and call the handler
                limiter.hit(key)
                logger.info(f"Rate limit check passed for user {user_id}")
                return await handler_func(update, context)
                
            except Exception as e:
                logger.error(f"Error in rate limiter: {str(e)}")
                # If there's an error in the rate limiter, still call the handler
                return await handler_func(update, context)
                
        return wrapper
    
    return decorator


def reset_rate_limit(user_id: str) -> None:
    """Reset the rate limit for a specific user."""
    key = f"telegram:{user_id}"
    if key in user_rate_limits:
        user_rate_limits[key] = False
        logger.info(f"Rate limit reset for user {user_id}")