from services.summary_service import SummaryService
from utils.localizer import get_localized_message
from utils.db_connection import get_db
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from handlers.speech_handler import handle_audio_request


async def handle_summary_request(update: Update, context: CallbackContext):
    """
    Handles the summary request after the transcript has been fetched.
    """
    user_language = context.user_data['user_language']
    transcript = context.user_data['transcript']
    video_id = context.user_data['video_id']
    video_duration = context.user_data['video_duration']
    session = context.user_data['session']

    # if not transcript or not video_id or not session: # TODO: logger.error

    # Get a DB session
    db = next(get_db())

    # Initialize the repositories and services
    summary_service = SummaryService(db)

    try:
        await update.message.reply_text(get_localized_message(user_language, "summary_msg"))

        # Step 1: Summarize the transcript
        summary_response = await summary_service.summarize_transcript(
            transcript=transcript,
            video_url=context.user_data['video_url'],
            video_id=video_id,
            video_duration=video_duration,
            user=context.user_data['user'],
            session=session,
            language_code=user_language
        )

        # Step 2: Check if the summary was generated successfully
        if not summary_response.is_success():
            await update.message.reply_text(get_localized_message(user_language, "no_content_err"))
            return

        # Step 3: Get the plain text summary
        plain_text_summary = summary_response.data.text_summary

        # Step 4: Add an inline button to trigger the audio conversion
        audio_button = get_localized_message(user_language, "audio_button")
        keyboard = [[InlineKeyboardButton(audio_button, callback_data="convert_to_audio")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send the summary along with the inline button to the user
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=plain_text_summary,
            reply_markup=reply_markup
        )

        # Store the summary and video ID in user_data for future use (audio conversion)
        context.user_data['summary'] = plain_text_summary
        context.user_data['summary_id'] = summary_response.data.summary_id  # Assuming the summary ID is returned
        context.user_data['video_id'] = video_id

    except Exception:
        # Handle any unexpected errors
        await update.message.reply_text(get_localized_message(user_language, "no_content_err"))

# Callback query handler to trigger speech conversion and remove the button
async def convert_to_audio_callback(update: Update, context: CallbackContext):
    """
    Handles the inline button callback to convert the summary to speech.
    """
    query = update.callback_query
    await query.answer()  # Acknowledge the callback query
    
    # Remove the inline keyboard by editing the message to have no reply markup
    await query.edit_message_reply_markup(reply_markup=None)

    # Proceed with speech conversion
    await handle_audio_request(update, context)