import sys
import httpx
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from tenacity import retry, stop_after_attempt, wait_fixed

from utils.logger import logger
from config.config import TOKEN
from handlers.transcript_handler import handle_video_link
from handlers.command_menu import start

# Add the /app directory to sys.path so Python can find utils, apis, handlers, etc.
sys.path.append('/app')

# Initialize FastAPI app
app = FastAPI()

# Initialize the global HTTP client with connection pooling
http_client = httpx.AsyncClient()

# Create Telegram application (bot) instance
telegram_application = Application.builder().token(TOKEN).build()

# Add handlers to the application
telegram_application.add_handler(CommandHandler("start", start))
telegram_application.add_handler(MessageHandler(filters.Entity("url"), handle_video_link))

# Clean up the connection pool on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    """Ensure connection pool is closed on shutdown."""
    await http_client.aclose()

# Retry configuration: Retry up to 3 times with a 2-second wait in between
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

async def initialize_application():
    """Ensure the Telegram application is initialized properly."""
    try:
        await telegram_application.initialize()
        logger.info("Telegram application initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing Telegram application: {str(e)}")
        raise

async def process_telegram_update(update_data):
    """Asynchronously process the Telegram update."""
    try:
        update = Update.de_json(update_data, telegram_application.bot)
        await initialize_application()
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