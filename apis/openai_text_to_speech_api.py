import asyncio
import io
from openai import RateLimitError, OpenAIError
from utils.logger import logger


async def convert_summary_to_speech(summary: str, client) -> io.BytesIO:
    """
    Converts the given summary to speech using the OpenAI TTS API and returns an in-memory MP3 file object.
    
    Args:
        summary (str): The text to be converted to speech.
        client (object): AsyncOpenAI client instance.
    
    Returns:
        io.BytesIO: In-memory MP3 file object, or None in case of an error.
    """
    try:
        logger.info("Attempting to convert the summary to speech using OpenAI TTS API...")
        
        # Create an in-memory file object to store the streaming response (MP3 data)
        audio_file = io.BytesIO()

        # Await the API response, but don't use `async with`
        response = await client.audio.speech.create(
            model="tts-1",  # Text-to-Speech model
            voice="alloy",  # Voice specification
            input=summary  # The summary text to be converted to speech
        )

        # Stream the audio content directly to the in-memory file in chunks
        for chunk in response.iter_bytes():  # Regular `for` loop
            audio_file.write(chunk)

        # Set the name and seek position of the in-memory file for proper Telegram handling
        audio_file.name = "summary.mp3"
        audio_file.seek(0)  # Rewind the file to the beginning

        logger.info("Successfully generated in-memory audio file.")
        return audio_file

    except (RateLimitError, OpenAIError, asyncio.TimeoutError) as e:
        logger.error(f"Error converting summary to speech: {e}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error during text-to-speech conversion: {e}")
        return None