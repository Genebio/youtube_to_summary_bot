import asyncio
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from utils.logger import logger
from config.constants import OPENAI_SUMMARY_PROMPT

# Retry configuration: Retry 3 times with a 2-second delay in between
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(Exception))
async def summarize_transcript(transcript: str, client, language: str = "en") -> str:
    """Summarizes the provided text using the OpenAI API and returns it in the user's locale."""
    try:
        # Log the attempt
        logger.info("Attempting to summarize the transcript using OpenAI API...")
        
        # Make the API call asynchronously
        completion = await asyncio.to_thread(
            client.chat.completions.create, 
            messages=[{
                "role": "user",
                "content": f"{OPENAI_SUMMARY_PROMPT}{language}:\n{transcript}"
            }],
            model="gpt-4o-mini"
        )

        # Extract the summary from the API response
        summary = completion.choices[0].message.content
        return summary

    except Exception as e:
        # Log the error before retrying or failing
        logger.error(f"Error during summarization: {e}")
        raise  # Re-raise the exception to trigger retry logic