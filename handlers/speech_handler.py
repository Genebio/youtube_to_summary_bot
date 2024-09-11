from apis.openai_text_to_speech_api import convert_summary_to_speech
from config.config import OPENAI_CLIENT


async def handle_speech_conversion(update, context):
    """Handles converting the summary to speech and sending it to the user."""
    summary = context.user_data.pop('summary', None)
    
    if summary:
        # Convert the summary to speech and get the in-memory MP3 file
        audio_file = await convert_summary_to_speech(summary, OPENAI_CLIENT)

        if audio_file:
            # Send the audio file to the user as a Telegram audio message
            await context.bot.send_audio(
                chat_id=update.message.chat_id,
                audio=audio_file,
                performer="@youtube_to_summary_bot",
                caption="✨ YouTube video summary ✨"
                )
        else:
            await update.message.reply_text("Error generating speech from summary.")
    else:
        await update.message.reply_text("No summary available for speech conversion.")