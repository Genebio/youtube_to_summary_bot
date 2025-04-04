import asyncio
from typing import Optional, Dict
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from youtube_transcript_api import (
    YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
)
from utils.logger import logger
from utils.cache import cached


# Retry configuration: Retry 3 times with a 2-second delay in between
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(Exception))
@cached(expiry=86400)  # Cache for 24 hours
async def fetch_youtube_transcript(video_id: str) -> Optional[Dict[str, str]]:
    """
    Asynchronously fetches the transcript (manual or auto-generated) for a YouTube video 
    and returns a dictionary with the transcript text and video duration.
    
    Results are cached for faster retrieval on subsequent requests for the same video.
    """
    try:
        logger.info(f"Fetching transcript for video ID: '{video_id}'")
        
        # Fetch the transcripts and their data in a single blocking thread
        transcripts = await asyncio.to_thread(YouTubeTranscriptApi.list_transcripts, video_id)
        
        # Prioritize manual transcripts over auto-generated ones
        transcript = next((t for t in transcripts if not t.is_generated), None)
        if not transcript:
            transcript = next((t for t in transcripts if t.is_generated), None)
        
        # If no transcript is found, log and return None
        if not transcript:
            logger.warning(f"No transcript found for video ID: '{video_id}'")
            return None
        
        transcript_data = transcript.fetch()
        if not transcript_data:
            logger.warning(f"Transcript data is empty for video ID: '{video_id}'")
            return None
        
        # Extract the transcript text
        transcript_text = ' '.join([entry['text'] for entry in transcript_data if 'text' in entry])
        
        # Get the last transcript entry's start time and duration, if available
        last_entry = transcript_data[-1] if transcript_data else None
        if last_entry and 'start' in last_entry and 'duration' in last_entry:
            video_duration = last_entry['start'] + last_entry['duration']
        else:
            logger.warning(f"Could not determine video duration for video ID: '{video_id}'")
            video_duration = None

        logger.info(f"Successfully fetched transcript for video ID: '{video_id}'")
        return {'transcript_text': transcript_text, 'video_duration': video_duration}
    
    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable) as e:
        logger.error(f"YouTube transcript API error for video ID '{video_id}': {str(e)}")
        return None

    except Exception as e:
        logger.error(f"Unexpected error during YouTube transcript API call for video ID '{video_id}': {str(e)}")
        raise