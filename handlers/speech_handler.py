from apis.openai_text_to_speech_api import convert_summary_to_speech
from config.config import OPENAI_CLIENT


async def handle_speech_conversion(update, context):
    """Handles converting the summary to speech and sending it to the user."""
    summary = context.user_data.pop('summary', None)

    # Check if update contains message or callback query
    message = update.message if update.message else update.callback_query.message
    
    if summary:
        # Inform the user that the bot is processing the request
        await message.reply_text("🎧 Please wait ... 🐢")

        # Convert the summary to speech and get the in-memory MP3 file
        audio_file = await convert_summary_to_speech(summary, OPENAI_CLIENT)

        if audio_file:
            # Send the audio file to the user as a Telegram audio message
            await context.bot.send_audio(
                chat_id=message.chat_id,
                audio=audio_file,
                title="✨ YouTube video summary ✨",
                performer="@youtube_to_summary_bot"
            )
        else:
            await message.reply_text("Error generating speech from summary.")
    else:
        await message.reply_text("No summary available for speech conversion.")