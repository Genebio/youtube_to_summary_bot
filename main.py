from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from utils.logger import logger
from config.config import TOKEN
from handlers import handle_video_link, start


# Initialize FastAPI app
app = FastAPI()

# Create Telegram application (bot) instance
application = Application.builder().token(TOKEN).build()

# Add handlers to the application
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.Entity("url"), handle_video_link))

async def initialize_application():
    """Ensure the Telegram application is initialized properly."""
    try:
        await application.initialize()
        logger.info("Application initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing application: {e}")
        raise

async def process_telegram_update(update_data):
    """Asynchronously process the Telegram update."""
    try:
        update = Update.de_json(update_data, application.bot)
        # Ensure the application is initialized before processing updates
        await initialize_application()
        # Process the update asynchronously
        await application.process_update(update)
    except Exception as e:
        logger.error(f"Error processing Telegram update: {e}, Update Data: {update_data}")
        raise  # Rethrow the error so it's still visible

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Handle incoming webhook requests from Telegram."""
    try:
        # Get the JSON body from the request
        update_data = await request.json()
        # Log the incoming request data for debugging
        logger.info(f"Incoming request: {update_data}")
        # Process the Telegram update asynchronously
        await process_telegram_update(update_data)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return {"error": str(e)}, 500