import re

from apis.youtube_api import fetch_transcript
from utils.logger import logger
from config.constants import VIDEO_ID_REGEX
from handlers import summary_handler


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

        if transcript.startswith("Error"):
            await update.message.reply_text(f"Error: {transcript}") #TODO
        else:
            # Send the transcript to the next handler (summary_handler)
            context.user_data['transcript'] = transcript
            
            # Trigger summary handler (summary_handler)
            await summary_handler.handle_summary_request(update, context)
    else:
        await update.message.reply_text(
            "⚠️ Oops! That doesn't seem like a valid YouTube link. Please double-check and try again. 😊"
            )