import sys
import httpx
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, PicklePersistence
)
from tenacity import retry, stop_after_attempt, wait_fixed
from contextlib import asynccontextmanager

from utils.logger import logger
from config.config import TOKEN
from handlers.transcript_handler import handle_video_link
from handlers.command_menu import start
from handlers.summary_handler import convert_to_audio_callback

# Add the /app directory to sys.path
sys.path.append('/app')

# Initialize FastAPI app
app = FastAPI()

# Global variables
http_client = None
telegram_application = None

# Lifespan context manager for app startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_client, telegram_application
    
    # Startup: Initialize HTTP client
    http_client = httpx.AsyncClient()
    
    # Initialize Telegram application
    persistence = PicklePersistence(filepath='bot_data.pkl')
    telegram_application = (
        Application.builder()
        .token(TOKEN)
        .persistence(persistence)
        .build()
    )
    
    # Register handlers
    telegram_application.add_handler(CommandHandler("start", start))
    telegram_application.add_handler(MessageHandler(filters.Entity("url"), handle_video_link))
    telegram_application.add_handler(
        CallbackQueryHandler(convert_to_audio_callback, pattern='convert_to_audio')
    )
    
    try:
        # Initialize bot without starting webhook
        await telegram_application.initialize()
        logger.info("Telegram application initialized successfully.")
        yield
    finally:
        # Shutdown
        if telegram_application:
            await telegram_application.shutdown()
            logger.info("Telegram application shut down successfully.")
        
        if http_client:
            await http_client.aclose()
            logger.info("HTTP client closed.")

# Add lifespan handler to FastAPI
app = FastAPI(lifespan=lifespan)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def fetch_data_with_retries(url: str):
    """Fetch data from a URL with retries."""
    if not http_client:
        raise RuntimeError("HTTP client not initialized")
        
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

async def process_telegram_update(update_data):
    """Asynchronously process the Telegram update."""
    if not telegram_application:
        raise RuntimeError("Telegram application not initialized")
        
    try:
        update = Update.de_json(update_data, telegram_application.bot)
        await telegram_application.process_update(update)
    except Exception as e:
        logger.error(f"Error processing Telegram update: {str(e)}, Update Data: {update_data}")
        raise

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Handle incoming webhook requests from Telegram."""
    try:
        update_data = await request.json()
        logger.info(f"Incoming request: {update_data}")
        await process_telegram_update(update_data)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {"error": str(e)}, 500