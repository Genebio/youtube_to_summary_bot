import re
from utils.logger import logger
from apis.youtube_api import fetch_transcript
from config.constants import VIDEO_ID_REGEX
from handlers.summary_handler import handle_summary_request


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
    
    if video_id:
        logger.info(f"Extracted video ID: '{video_id}' from URL: '{url}'")
        transcript = await fetch_transcript(video_id)

        if transcript is None:
            # Send the user-friendly error message
            await update.message.reply_text(
                "⚠️ Sorry, we can't get insights from this video. Try another one? 🎥"
                )
        else:
            context.user_data['transcript'] = transcript
            # Pass the transcript directly to the summary handler
            await handle_summary_request(update, context)
    else:
        await update.message.reply_text(
            "⚠️ Oops! That doesn't seem like a valid YouTube link. Please double-check and try again. 😊"
        )