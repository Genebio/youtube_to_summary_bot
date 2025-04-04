import sys
import httpx
from telegram import Update
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from tenacity import retry, stop_after_attempt, wait_fixed
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import Dict, Any

from utils.logger import logger
from utils.cache import check_redis_connection
from config.config import TOKEN, RATE_LIMIT_REQUESTS, RATE_LIMIT_PERIOD
from handlers.url_handler import handle_video_link
from handlers.command_menu import start

# Add the /app directory to sys.path so Python can find utils, apis, handlers, etc.
sys.path.append('/app')

# Initialize FastAPI app with metadata for OpenAPI documentation
app = FastAPI(
    title="YouTube Summary Bot API",
    description="""
    A Telegram bot that summarizes YouTube videos using AI.
    
    ## Features:
    
    - Fetches transcripts from YouTube videos
    - Generates concise summaries using OpenAI
    - Supports multiple languages
    - Stores summaries for quick retrieval
    - Implements rate limiting and caching
    """,
    version="1.0.0",
    contact={
        "name": "YouTube Summary Bot",
        "url": "https://t.me/your_bot_username"
    },
)

# Set up API rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify actual origins instead of "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the global HTTP client with connection pooling
http_client = httpx.AsyncClient()

# Create Telegram application (bot) instance
telegram_application = Application.builder().token(TOKEN).build()

# Register bot handlers, including the callback handler for inline buttons
def register_handlers(application):
    """Register all command and callback handlers."""
    # Register start command and video link message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Entity("url"), handle_video_link))

# Call the function to register handlers
register_handlers(telegram_application)

# Clean up the HTTP connection pool on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    """Ensure connection pool and Telegram application are closed on shutdown."""
    # Check if the Telegram application is running before stopping it
    if telegram_application.running:
        await telegram_application.stop()
        logger.info("Telegram application stopped successfully.")
    else:
        logger.info("Telegram application was not running.")
        
    # Close the HTTP client connection
    await http_client.aclose()
    logger.info("HTTP client closed.")

# Startup event to check connections to external services
@app.on_event("startup")
async def startup_event():
    """Check connections to external services on startup."""
    # Check Redis connection
    redis_available = await check_redis_connection()
    if not redis_available:
        logger.warning("Redis is not available, caching will be disabled")
    else:
        logger.info("Redis connection established")
    
    # Log rate limit settings
    logger.info(f"Rate limiting configured: {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_PERIOD} seconds")

# Retry configuration: Retry up to 3 times with a 2-second wait in between attempts
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def fetch_data_with_retries(url: str):
    """Fetch data from a URL with retries."""
    try:
        response = await http_client.get(url)
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        logger.error(f"An error occurred while requesting {url}: {str(e)}")
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"Error response {e.response.status_code} while requesting {url}: {str(e)}")
        raise

# Initialize Telegram bot application
async def initialize_application():
    """Ensure the Telegram application is initialized properly."""
    try:
        await telegram_application.initialize()
        logger.info("Telegram application initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing Telegram application: {str(e)}")
        raise

# Process the incoming update from Telegram
async def process_telegram_update(update_data):
    """Asynchronously process the Telegram update."""
    try:
        update = Update.de_json(update_data, telegram_application.bot)
        await initialize_application()
        await telegram_application.process_update(update)
    except Exception as e:
        logger.error(f"Error processing Telegram update: {str(e)}")
        raise

# FastAPI webhook to handle incoming Telegram updates
@app.post("/webhook", 
    summary="Telegram Webhook Endpoint",
    description="Handles incoming webhook requests from Telegram and processes bot commands",
    response_description="Status of the webhook processing",
    responses={
        200: {"description": "Webhook processed successfully"},
        400: {"description": "Bad request format"},
        429: {"description": "Too many requests (rate limited)"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit(f"{RATE_LIMIT_REQUESTS}/{RATE_LIMIT_PERIOD}second")
async def telegram_webhook(request: Request):
    """Handle incoming webhook requests from Telegram."""
    try:
        update_data = await request.json()
        logger.info(f"Incoming request: {update_data}")
        await process_telegram_update(update_data)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e)}
        )

# Health check endpoint
@app.get("/health", 
    summary="Health Check Endpoint",
    description="Returns the health status of the API and its dependencies",
    response_description="Health status information"
)
@limiter.limit("10/minute")
async def health_check(request: Request) -> Dict[str, Any]:
    """Check the health of the service and its dependencies."""
    health_info = {
        "status": "ok",
        "version": "1.0.0",
        "dependencies": {
            "redis": "ok" if await check_redis_connection() else "unavailable"
        }
    }
    return health_info

# API documentation redirect
@app.get("/", include_in_schema=False)
async def root():
    """Redirect to the API documentation."""
    return {"message": "Welcome to YouTube Summary Bot API. Check /docs for API documentation."}