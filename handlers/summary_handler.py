from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from apis.openai_summary_api import summarize_transcript
from config.config import OPENAI_CLIENT
from handlers.speech_handler import handle_speech_conversion
from utils.formatter import clean_markdown_symbols
from utils.localizer import get_localized_message


async def handle_summary_request(update, context):
    """Handles summarization of the transcript."""
    user_language = update.effective_user.language_code if update.effective_user.language_code else 'en'
    summary_msg = get_localized_message(user_language, "summary_msg")
    await context.bot.send_message(chat_id=update.message.chat_id, text=summary_msg)
    
    transcript = context.user_data.pop('transcript', None)
    
    # Call the OpenAI API to summarize the transcript
    summary = await summarize_transcript(transcript, OPENAI_CLIENT, user_language)
    plain_text_summary = clean_markdown_symbols(summary)

    audio_button = get_localized_message(user_language, "audio_button")
    keyboard = [[InlineKeyboardButton(audio_button, callback_data="convert_to_audio")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
  
    # Send a summary with the inline button
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=plain_text_summary,
        reply_markup=reply_markup
    )
    
    # Store the summary in user data to pass to the speech handler
    context.user_data['summary'] = plain_text_summary

# Callback query handler to trigger speech conversion and remove the button
async def convert_to_audio_callback(update, context):
    """Handles the inline button callback to convert summary to speech."""
    query = update.callback_query
    await query.answer()  # Acknowledge the callback query
    
    # Remove the inline keyboard by editing the message to have no reply markup
    await query.edit_message_reply_markup(reply_markup=None)

    # Proceed with speech conversion
    await handle_speech_conversion(update, context)
