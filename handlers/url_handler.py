from  asyncio import sleep
from apis.fetch_transcript import fetch_youtube_transcript
from apis.summary import summarize_transcript
from repositories.user_repository import UserRepository
from repositories.session_repository import SessionRepository
from repositories.summary_repository import SummaryRepository
from utils.formatter import extract_video_id, truncate_by_token_count, remove_markdown_v2_symbols
from utils.localizer import get_localized_message
from utils.db_connection import get_db, init_db
from utils.datetime_utils import format_timestamp_for_display
from utils.rate_limiter import rate_limited
from utils.cache import check_redis_connection
from telegram import Update
from telegram.ext import CallbackContext
from config.config import OPENAI_CLIENT
from config.summary_config import SummaryConfig
from utils.logger import logger

@rate_limited()  # Apply rate limiting to the handler
async def handle_video_link(update: Update, context: CallbackContext):
    """
    Handler for YouTube video links in Telegram messages.
    
    Processes the link to:
    1. Extract the video ID
    2. Check if a summary exists in the database
    3. Fetch the transcript if needed
    4. Generate a summary using OpenAI if needed
    5. Return the summary to the user
    
    Rate limiting is applied to prevent abuse.
    """
    user_language = update.effective_user.language_code if update.effective_user.language_code else 'en'
    video_url = update.message.text
    video_id = extract_video_id(video_url)
    
    if not video_id:
        logger.warning(f"Invalid video link provided: {video_url}")
        await update.message.reply_text(get_localized_message(user_language, "no_valid_link_err"))
        return

    session = None
    session_repo = None

    try:
        # Check Redis connection
        redis_available = await check_redis_connection()
        if not redis_available:
            logger.warning("Redis is not available, caching will be disabled")
        
        # Initialize database
        init_db()
        db = next(get_db())
        
        # Get or create user
        user_repo = UserRepository(db)
        user = user_repo.get_or_create_user(
            username=update.message.from_user.username or "unknown",
            first_name=update.message.from_user.first_name or "",
            last_name=update.message.from_user.last_name or "",
            language_code=user_language
        )
        
        # Create session to track this request
        session_repo = SessionRepository(db)
        session = session_repo.create_session(user_id=user.user_id)

        # Step 0: Check if summary already exists in database
        summary_repo = SummaryRepository(db)
        existing_summary = summary_repo.fetch_summary(video_id, user_language)
        
        await update.message.reply_text("🔍 ...")

        if existing_summary:
            logger.info(f"Using existing summary for video ID: {video_id}")
            session_repo.end_session(session, end_reason="Fetched existing summary")
            await sleep(1)
            await update.message.reply_text(get_localized_message(user_language, "summary_msg"))
            await sleep(2)  # Reduced from 3 to 2 seconds
            await update.message.reply_text(existing_summary)
            return

        # Step 1: Fetch video transcript
        transcript_data = await fetch_youtube_transcript(video_id)
        
        if not transcript_data or 'transcript_text' not in transcript_data:
            logger.error(f"No transcript fetched for video ID: {video_id}")
            session_repo.end_session(session, end_reason="No transcript fetched")
            await update.message.reply_text(get_localized_message(user_language, "no_content_err"))
            return
            
        transcript = transcript_data.get('transcript_text')
        video_duration = transcript_data.get('video_duration')

        # Step 2: Summarize transcript
        await update.message.reply_text(get_localized_message(user_language, "summary_msg"))
        
        summary_data = await summarize_transcript(
            transcript=truncate_by_token_count(transcript),
            client=OPENAI_CLIENT,
            language=user_language
        )
        
        if summary_data.get('error'):
            logger.error(f"Error in summarization for video ID {video_id}: {summary_data.get('error')}. Details: {summary_data.get('details', 'No details provided.')}")
            session_repo.end_session(session, end_reason=f"Summarization error: {summary_data.get('error')}")
            await update.message.reply_text(get_localized_message(user_language, "general_error_msg"))
            return
        
        summary = remove_markdown_v2_symbols(summary_data['summary'])
        await update.message.reply_text(summary)

        # Save the summary to database for future requests
        summary_repo.save_summary(
            user=user, session=session, video_url=video_url, video_id=video_id,
            language_code=user_language, text_summary=summary, summary_version=SummaryConfig.get_version(),
            video_duration=video_duration, summary_model=SummaryConfig.get_model(), 
            input_tokens=summary_data['input_tokens'], output_tokens=summary_data['output_tokens']
        )
        
        # End session properly
        if session_repo and session:
            end_session_result = session_repo.end_session(session, end_reason="Summary generated and saved")
            if not end_session_result:
                logger.error("Failed to end session properly")
            else:
                logger.info(f"Session ended at: {format_timestamp_for_display(end_session_result.shutdown_time)}")
          
    except Exception as e:
        logger.error(f"Unexpected error in handle_video_link: {str(e)}")
        if session_repo and session:
            end_session_result = session_repo.end_session(session, end_reason=f"Unexpected error: {str(e)}")
            if not end_session_result:
                logger.error("Failed to end session properly after an error")
            else:
                logger.info(f"Session ended at: {format_timestamp_for_display(end_session_result.shutdown_time)}")
        await update.message.reply_text(get_localized_message(user_language, "general_error_msg"))