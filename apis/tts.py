# import asyncio
# import io
# from openai import RateLimitError, OpenAIError
# from utils.logger import logger
# from utils.formatter import ServiceResponse
# from config.constants import OPENAI_TTS_MODEL, OPENAI_TTS_VOICE


# async def convert_summary_to_speech(summary: str, client) -> ServiceResponse:
#     """
#     Converts the given summary to speech using the OpenAI TTS API and returns an in-memory MP3 file object 
#     along with TTS model details.

#     Args:
#         summary (str): The text to be converted to speech.
#         client (object): AsyncOpenAI client instance.

#     Returns:
#         ServiceResponse: Contains in-memory MP3 file object, TTS model, and token usage in 'data', or an error message.
#     """
#     try:
#         logger.info("Attempting to convert the summary to speech using OpenAI TTS API...")

#         # Create an in-memory file object to store the streaming response (MP3 data)
#         audio_file = io.BytesIO()

#         # Await the API response, but don't use `async with`
#         response = await client.audio.speech.create(
#             model=OPENAI_TTS_MODEL,  # Text-to-Speech model
#             voice=OPENAI_TTS_VOICE,  # Voice specification
#             input=summary  # The summary text to be converted to speech
#         )

#         # Stream the audio content directly to the in-memory file in chunks
#         for chunk in response.iter_bytes():
#             audio_file.write(chunk)

#         # Set the name and seek position of the in-memory file for proper Telegram handling
#         audio_file.name = "summary.mp3"
#         audio_file.seek(0)  # Rewind the file to the beginning

#         logger.info("Successfully generated in-memory audio file.")
        
#         # Extract TTS model and token usage from response (adjust based on actual response structure)
#         tts_model = response.model
#         tts_tokens = response.tokens_used

#         return ServiceResponse(data={
#             "audio_file": audio_file,
#             "tts_model": tts_model,
#             "tts_tokens": tts_tokens
#         })

#     except (RateLimitError, OpenAIError, asyncio.TimeoutError) as e:
#         logger.error(f"Error converting summary to speech: {e}")
#         return ServiceResponse(error=f"Error converting summary to speech: {str(e)}")

#     except Exception as e:
#         logger.error(f"Unexpected error during text-to-speech conversion: {e}")
#         return ServiceResponse(error=f"Unexpected error during text-to-speech conversion: {str(e)}")