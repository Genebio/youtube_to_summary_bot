import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters
from bot.config import TOKEN
from bot.handlers import handle_video_link, start

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Command handler for /start command
    start_handler = CommandHandler("start", start)
    
    # Message handler for video links
    summary_handler = MessageHandler(filters.Entity("url"), handle_video_link)

    application.add_handler(start_handler)
    application.add_handler(summary_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()