from apis.fetch_transcript import fetch_youtube_transcript
from apis.summary import summarize_transcript
from repositories.user_repository import UserRepository
from repositories.session_repository import SessionRepository
from repositories.summary_repository import SummaryRepository
from utils.formatter import extract_video_id, truncate_by_token_count
from utils.localizer import get_localized_message
from utils.db_connection import get_db, init_db
from telegram import Update
from telegram.ext import CallbackContext
from config.config import OPENAI_CLIENT
from utils.logger import logger

async def handle_video_link(update: Update, context: CallbackContext):
    user_language = update.effective_user.language_code if update.effective_user.language_code else 'en'
    video_url = update.message.text
    video_id = extract_video_id(video_url)
    
    if not video_id:
        logger.warning(f"Invalid video link provided: {video_url}")
        await update.message.reply_text(get_localized_message(user_language, "no_valid_link_err"))
        return

    try:
        init_db()
        db = next(get_db())
        user_repo = UserRepository(db)
        user = user_repo.get_or_create_user(
            username=update.message.from_user.username,
            first_name=update.message.from_user.first_name,
            last_name=update.message.from_user.last_name,
            language_code=user_language
        )
        
        session_repo = SessionRepository(db)
        session = session_repo.create_session(user_id=user.user_id)

        # Step 0: fetch existing summary
        summary_repo = SummaryRepository(db)
        existing_summary = summary_repo.fetch_summary(video_id, user_language)
        
        if existing_summary:
            session_repo.end_session(session, end_reason="Fetched existing summary")
            await update.message.reply_text(existing_summary)
            return

        await update.message.reply_text("🔍 ...")

        # Step 1: Fetch video transcript
        transcript_data = await fetch_youtube_transcript(video_id)
        transcript, video_duration = transcript_data.get('transcript_text'), transcript_data.get('video_duration')
        
        if not transcript:
            logger.error(f"No transcript fetched for video ID: {video_id}")
            session_repo.end_session(session, end_reason="No transcript fetched")
            await update.message.reply_text(get_localized_message(user_language, "no_content_err"))
            return

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
        
        summary = summary_data['summary']
        await update.message.reply_text(summary)

        summary_repo.save_summary(
            user=user, session=session, video_url=video_url, video_id=video_id,
            language_code=user_language, text_summary=summary,
            video_duration=video_duration, summary_model=summary_data['summary_model'],
            input_tokens=summary_data['input_tokens'], output_tokens=summary_data['output_tokens']
        )
        
        session_repo.end_session(session, end_reason="Summary generated and saved")
       
    except Exception as e:
        logger.error(f"Unexpected error in handle_video_link: {str(e)}")
        if 'session' in locals() and 'session_repo' in locals():
            session_repo.end_session(session, end_reason=f"Unexpected error: {str(e)}")
        await update.message.reply_text(get_localized_message(user_language, "general_error_msg"))