import logging
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

@functions_framework.http
async def telegram_bot(request):
    """HTTP Cloud Function to handle Telegram updates."""
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.process_update(update)
    return "ok"

if __name__ == "__main__":
    # Use the built-in webhook handling from python-telegram-bot
    application.run_webhook(
        listen="0.0.0.0",
        port=8080,
        webhook_url="https://europe-west10-telegram-bots-9471.cloudfunctions.net/youtube_to_summary_bot",
    )