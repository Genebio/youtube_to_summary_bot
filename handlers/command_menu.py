from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command."""
    await update.message.reply_text(
        text=(
            "*What can this bot do?*\n\n"
            "Get quick video summaries:\n\n"
            "1\\. Send a YouTube link\n"
            "2\\. Receive a concise summary\n"
            "3\\. Save time and grasp key insights fast\n\n"
            "💡 *Tip:* Perfect for quick research or deciding what to watch\\.\n\n"
            "🚀 *Ready? Drop a link to get started\\!*"
        ),
        parse_mode="MarkdownV2"
    )