from services.summary_service import SummaryService
from utils.localizer import get_localized_message
from utils.db_connection import get_db


async def handle_audio_request(update, context):
    """
    Handles the request to convert a summary to audio.
    """
    message = update.message if update.message else update.callback_query.message
    chat_id = message.chat_id
    user_language = context.user_data['user_language']
    summary_id = context.user_data['summary_id']
    summary_text = context.user_data['summary']

    if not summary_id or not summary_text:
        no_audio_err = get_localized_message(user_language, "no_audio_err")
        await context.bot.send_message(chat_id=chat_id, text=no_audio_err)
        return

    # Get a DB session
    db = next(get_db())

    # Initialize the summary service
    summary_service = SummaryService(db)

    try:
        audio_msg = get_localized_message(user_language, "audio_msg")
        await context.bot.send_message(chat_id=chat_id, text=audio_msg)

        # Step 1: Convert the summary to audio
        audio_response = await summary_service.convert_summary_to_audio(summary_id, summary_text, user=context.user_data['user'])

        # Step 2: Check if the audio was generated successfully
        if not audio_response.is_success():
            audio_expired_err = get_localized_message(user_language, "audio_expired_err")
            await context.bot.send_message(chat_id=chat_id, text=audio_expired_err)
            return

        # Step 3: Extract the generated audio file and send it to the user
        audio_file = audio_response.data['audio_file']  # Assuming 'audio_file' is returned from the service

        await context.bot.send_audio(
            chat_id=message.chat_id,
            audio=audio_file,
            title="YouTube video summary",
            performer="youtube_to_summary_bot"
        )

    except Exception as e:
        # Handle any unexpected errors
        no_audio_err = get_localized_message(user_language, "no_audio_err")
        await context.bot.send_message(chat_id=chat_id, text=no_audio_err)