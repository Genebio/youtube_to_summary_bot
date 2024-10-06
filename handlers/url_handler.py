from apis.fetch_transcript import fetch_youtube_transcript
from apis.summary import summarize_transcript
from repositories.user_repository import UserRepository
from repositories.session_repository import SessionRepository
from repositories.summary_repository import SummaryRepository
from utils.formatter import extract_video_id, truncate_by_token_count
from utils.localizer import get_localized_message
from utils.db_connection import get_db
from telegram import Update
from telegram.ext import CallbackContext
from config.config import OPENAI_CLIENT


async def handle_video_link(update: Update, context: CallbackContext):
    video_url = update.message.text
    video_id = extract_video_id(video_url)
    if not video_id:
        no_valid_link_err = get_localized_message(user_language, "no_valid_link_err")
        await update.message.reply_text(no_valid_link_err)
        return
    user_language = update.effective_user.language_code if update.effective_user.language_code else 'en'
    try:
        # Get a DB session
        db = next(get_db())

        # Get or create the user by their username
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
        summary = summary_repo.fetch_summary(video_id, user_language)
        if summary:
            session_repo.end_session(session, end_reason="Fetched existing summary")
            await update.message.reply_text(summary)
            return

        await update.message.reply_text("🔍 ...")

        # Step 1: Fetch video transcript
        transcript_data = await fetch_youtube_transcript(video_id)
        transcript, video_duration = transcript_data['transcript_text'], transcript_data['video_duration']
        if not transcript:
            session_repo.end_session(session, end_reason="No transcript fetched")
            no_content_err = get_localized_message(user_language, "no_content_err")
            await update.message.reply_text(no_content_err)
            return

        # Step 2: Summarize transcript
        await update.message.reply_text(get_localized_message(user_language, "summary_msg"))
        summary_data = await summarize_transcript(
            transcript=truncate_by_token_count(transcript),
            client=OPENAI_CLIENT,
            language_code=user_language
            )
        summary, input_tokens, output_tokens, summary_model = (
            summary_data['summary'], summary_data['input_tokens'],
            summary_data['output_tokens'], summary_data['summary_model']
            )
        if not summary:
            session_repo.end_session(session, end_reason="Summary not generated")
            await update.message.reply_text(get_localized_message(user_language, "no_content_err"))
            return
        
        await update.message.reply_text(summary)

        # Step 3: Save summary to db
        summary_repo.save_summary(user=user, session=session, video_url=video_url, video_id=video_id,
                                  language_code=user_language, text_summary=summary,
                                  video_duration=video_duration, summary_model=summary_model,
                                  input_tokens=input_tokens, output_tokens=output_tokens)
        session_repo.end_session(session, end_reason="Summary generated")
       
    except Exception as e:
        session_repo.end_session(session, end_reason="Unexpected error" + str(e))
        await update.message.reply_text(get_localized_message(user_language, "no_content_err"))
