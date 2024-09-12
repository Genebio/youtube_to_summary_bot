import re
from utils.logger import logger
from apis.youtube_transcript_api import fetch_transcript
from config.constants import VIDEO_ID_REGEX
from handlers.summary_handler import handle_summary_request
from utils.formatter import truncate_by_token_count
from utils.localizer import get_localized_message


def extract_video_id(url: str) -> str:
    """
    Extracts the video ID from a variety of YouTube URL formats.
    """
    match = re.search(VIDEO_ID_REGEX, url)
    return match.group(1) if match else None

async def handle_video_link(update, context):
    """
    Handles incoming YouTube video links sent by the user.
    Extracts the video ID and fetches the transcript.
    """
    url = update.message.text
    video_id = extract_video_id(url)
    logger.info(f"Extracted video ID: '{video_id}' from URL: '{url}'")

    user_language = update.effective_user.language_code if update.effective_user.language_code else 'en'

    if video_id:
        await update.message.reply_text("🔍 ...")
        transcript = await fetch_transcript(video_id)
        

        if transcript is None:
            # Send the user-friendly error message
            no_transcript_err = get_localized_message(user_language, "no_transcript_err")
            await update.message.reply_text(no_transcript_err)
        else:
            context.user_data['transcript'] = truncate_by_token_count(transcript)
            await handle_summary_request(update, context)
    else:
        no_valid_link_err = get_localized_message(user_language, "no_valid_link_err")
        await update.message.reply_text(no_valid_link_err)