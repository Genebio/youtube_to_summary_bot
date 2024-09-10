import asyncio
from youtube_transcript_api import (
    YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
)
from utils.logger import logger

async def fetch_transcript(video_id: str, retries: int = 3, delay: float = 2.0) -> str:
    """
    Asynchronously fetches the transcript (manual or auto-generated) for a YouTube video,
    with a specified number of retries and a delay between retries.
    """
    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Attempt {attempt} to fetch transcript for video ID: {video_id}")
            
            # Fetch the list of transcripts asynchronously
            transcripts = await asyncio.to_thread(YouTubeTranscriptApi.list_transcripts, video_id)

            # Log the raw transcripts object for debugging
            logger.info(f"Fetched transcripts object: {transcripts}")

            # Prioritize manual transcripts over auto-generated ones
            transcript = next((t for t in transcripts if not t.is_generated), None)
            if not transcript:
                transcript = next((t for t in transcripts if t.is_generated), None)

            if transcript:
                # Fetch the transcript content
                transcript_data = await asyncio.to_thread(transcript.fetch)
                return ' '.join([entry['text'] for entry in transcript_data])

            logger.warning(f"No transcript found for video ID: '{video_id}'")
            return None  # Return None to signify failure

        except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable) as e:
            logger.warning(f"Transcript error for video ID '{video_id}': {str(e)}")
            return None  # Return None to signify failure

        except Exception as e:
            logger.error(f"Error on attempt {attempt} while fetching transcript for video ID '{video_id}': {e}")
            if attempt < retries:
                logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)  # Wait before retrying
            else:
                logger.error(f"Failed to fetch transcript after {retries} attempts.")
                return None  # Return None after exceeding retries