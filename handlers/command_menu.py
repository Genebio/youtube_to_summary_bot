from telegram import Update
from telegram.ext import ContextTypes
from utils.localizer import get_localized_message


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command."""
    user_language = update.effective_user.language_code if update.effective_user.language_code else 'en'
    start_msg = get_localized_message(user_language, "start_msg")
    await update.message.reply_text(start_msg)