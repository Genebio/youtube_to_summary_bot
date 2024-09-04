import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import functions_framework
from config import TOKEN
from handlers import handle_video_link, start

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize the application globally so it can be reused across requests
application = Application.builder().token(TOKEN).build()

# Add handlers to the application
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.Entity("url"), handle_video_link))

async def initialize_application():
    """Ensure the application is initialized properly."""
    await application.initialize()

def process_telegram_update(update_data):
    """Synchronously process the Telegram update."""
    update = Update.de_json(update_data, application.bot)
    # Ensure the application is initialized before processing updates
    asyncio.run(initialize_application())
    # Run the asynchronous function in a synchronous manner
    asyncio.run(application.process_update(update))

@functions_framework.http
def telegram_bot(request):
    """HTTP Cloud Function to handle Telegram updates."""
    if request.method == "POST":
        try:
            # Get the JSON from the request
            update_data = request.get_json(force=True)
            # Log the incoming request data for debugging
            logger.info(f"Incoming request: {update_data}")
            # Process the update data using the synchronous wrapper
            process_telegram_update(update_data)
            return "ok", 200
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return f"Error: {e}", 500