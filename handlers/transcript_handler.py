from repositories.user_repository import UserRepository
from services.summary_service import SummaryService
from utils.localizer import get_localized_message
from utils.db_connection import get_db
from telegram import Update
from telegram.ext import CallbackContext

async def handle_video_link(update: Update, context: CallbackContext):
    """
    Handles incoming YouTube video links sent by the user.
    Fetches/creates the user, processes the video URL, and fetches the transcript.
    """
    chat_id = update.message.chat_id
    user_language = update.effective_user.language_code if update.effective_user.language_code else 'en'
    video_url = update.message.text

    # Get a DB session
    db = next(get_db())

    # Initialize the repositories and services
    user_repo = UserRepository(db)
    summary_service = SummaryService(db)

    # Fetch or create the user based on chat_id (assuming chat_id is the user_id)
    user = user_repo.get_user_by_id(chat_id)
    if not user:
        user = user_repo.create_user(
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
            last_name=update.effective_user.last_name,
            language_code=user_language
        )

    try:
        await update.message.reply_text("🔍 Processing video...")

        # Step 1: Fetch the transcript for the video
        transcript_response = await summary_service.fetch_transcript(video_url, user)

        # Step 2: Check if the video URL is valid
        if not transcript_response.is_success():
            no_valid_link_err = get_localized_message(user_language, "no_valid_link_err")
            await update.message.reply_text(no_valid_link_err)
            return

        # Step 3: Check if the transcript was fetched successfully
        if not transcript_response.data:
            no_content_err = get_localized_message(user_language, "no_content_err")
            await update.message.reply_text(no_content_err)
            return

        # Step 4: Store the transcript and session in context.user_data for further processing
        context.user_data['transcript'] = transcript_response.data['transcript']
        context.user_data['video_id'] = transcript_response.data['video_id']
        context.user_data['video_duration'] = transcript_response.data['video_duration']
        context.user_data['session'] = transcript_response.data['session']
        context.user_data['user_language'] = user_language

    except Exception as e:
        # Handle any unexpected errors
        await update.message.reply_text(get_localized_message(user_language, "no_content_err"))