import sys
import httpx
from telegram import Update
from fastapi import FastAPI, Request
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from tenacity import retry, stop_after_attempt, wait_fixed

from utils.logger import logger
from config.config import TOKEN
from handlers.url_handler import handle_video_link
from handlers.command_menu import start

# Add the /app directory to sys.path so Python can find utils, apis, handlers, etc.
sys.path.append('/app')

# Initialize FastAPI app
app = FastAPI()

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
        logger.error(f"Error processing Telegram update: {str(e)}, Update Data: {update_data}")
        raise

# FastAPI webhook to handle incoming Telegram updates
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