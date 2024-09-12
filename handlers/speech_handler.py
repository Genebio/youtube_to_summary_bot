from apis.openai_text_to_speech_api import convert_summary_to_speech
from config.config import OPENAI_CLIENT
from utils.localizer import get_localized_message


async def handle_speech_conversion(update, context):
    """Handles converting the summary to speech and sending it to the user."""
    summary = context.user_data.pop('summary', None)

    # Check if update contains message or callback query
    message = update.message if update.message else update.callback_query.message
    user_language = update.effective_user.language_code if update.effective_user.language_code else 'en'
    
    if summary:
        # Inform the user that the bot is processing the request
        audio_msg = get_localized_message(user_language, "audio_msg")
        await message.reply_text(audio_msg)

        # Convert the summary to speech and get the in-memory MP3 file
        audio_file = await convert_summary_to_speech(summary, OPENAI_CLIENT)

        if audio_file:
            # Send the audio file to the user as a Telegram audio message
            await context.bot.send_audio(
                chat_id=message.chat_id,
                audio=audio_file,
                title="YouTube video summary",
                performer="@youtube_to_summary_bot"
            )
        else:
            no_audio_err = get_localized_message(user_language, "no_audio_err")
            await message.reply_text(no_audio_err)
    else:
        audio_expired_err = get_localized_message(user_language, "audio_expired_err")
        await message.reply_text(audio_expired_err)