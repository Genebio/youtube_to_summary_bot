import asyncio
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from youtube_transcript_api import (
    YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
)
from utils.logger import logger
from utils.formatter import ServiceResponse


# Retry configuration: Retry 3 times with a 2-second delay in between
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(Exception))
async def fetch_youtube_transcript(video_id: str) -> ServiceResponse:
    """Asynchronously fetches the transcript (manual or auto-generated) for a YouTube video and returns a ServiceResponse."""
    try:
        logger.info(f"Fetching transcript for video ID: '{video_id}'")
        transcripts = await asyncio.to_thread(YouTubeTranscriptApi.list_transcripts, video_id)
        
        # Prioritize manual transcripts over auto-generated ones
        transcript = next((t for t in transcripts if not t.is_generated), None)
        if not transcript:
            transcript = next((t for t in transcripts if t.is_generated), None)
        
        if transcript:
            transcript_data = await asyncio.to_thread(transcript.fetch)
            transcript_text = ' '.join([entry['text'] for entry in transcript_data])
            return ServiceResponse(data=transcript_text)
        
        logger.warning(f"No transcript found for video ID: '{video_id}'")
        return ServiceResponse(error="No transcript found")
    
    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable) as e:
        logger.warning(f"Transcript error for video ID '{video_id}': {str(e)}")
        return ServiceResponse(error=f"Transcript error: {str(e)}")

    except Exception as e:
        logger.error(f"An unexpected error occurred while fetching the transcript for video ID '{video_id}': {str(e)}")
        return ServiceResponse(error=f"Unexpected error: {str(e)}")