import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai import RateLimitError, OpenAIError
from utils.logger import logger
from config.constants import OPENAI_SUMMARY_PROMPT

# Retry configuration: Exponential backoff with retries for specific exceptions
@retry(
    stop=stop_after_attempt(3),  # Retry up to 3 times
    wait=wait_exponential(multiplier=1, min=2, max=10),  # Exponential backoff starting at 2s, max 10s
    retry=retry_if_exception_type((asyncio.TimeoutError, OpenAIError, RateLimitError))  # Retry on transient issues
)
async def summarize_transcript(transcript: str, client, language: str = "en") -> str:
    """Summarizes the provided text using the OpenAI API asynchronously, with retry logic."""
    try:
        logger.info("Attempting to summarize the transcript using OpenAI API...")

        # Make the API call asynchronously (directly await the client call)
        completion = await client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"{OPENAI_SUMMARY_PROMPT}. Present the summary in '{language}' language:\n\n{transcript}"
            }],
            model="gpt-4o-mini"
        )

        # Extract the summary from the API response
        summary = completion.choices[0].message.content
        return summary

    except RateLimitError as e:
        logger.error(f"Rate limit exceeded: {e}")
        raise  # Reraise to trigger retry logic

    except OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        raise  # Reraise to trigger retry logic

    except asyncio.TimeoutError as e:
        logger.error(f"Timeout occurred during summarization: {e}")
        raise  # Reraise to trigger retry logic

    except Exception as e:
        logger.error(f"Unexpected error during summarization: {e}")
        raise  # Reraise to trigger retry logic for unexpected errors