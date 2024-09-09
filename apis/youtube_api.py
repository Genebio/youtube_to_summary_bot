import asyncio
from youtube_transcript_api import (
    YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
    )
from utils.logger import logger


async def fetch_transcript(video_id: str) -> str:
    """Asynchronously fetches the transcript (manual or auto-generated) for a YouTube video."""
    try:
        transcripts = await asyncio.to_thread(YouTubeTranscriptApi.list_transcripts, video_id)
        
        # Prioritize manual transcripts over auto-generated ones
        transcript = next((t for t in transcripts if not t.is_generated), None)
        if not transcript:
            transcript = next((t for t in transcripts if t.is_generated), None)
        
        if transcript:
            transcript_data = await asyncio.to_thread(transcript.fetch)
            return ' '.join([entry['text'] for entry in transcript_data])
        return "No transcript found."
    
    except NoTranscriptFound:
        return "No transcript found for this video."
    except TranscriptsDisabled:
        return "Transcripts are disabled for this video."
    except VideoUnavailable:
        return "The video is unavailable."
    except Exception as e:
        logger.error(f"An error occurred while fetching the transcript: {e}")
        return f"An unexpected error occurred: {str(e)}"