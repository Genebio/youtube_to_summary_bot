import asyncio
from openai import RateLimitError, OpenAIError
from utils.logger import logger
from config.constants import OPENAI_SUMMARY_PROMPT, OPENAI_SUMMARY_MODEL


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
            model=OPENAI_SUMMARY_MODEL
        )

        # Extract the summary from the API response
        summary = completion.choices[0].message.content
        return summary

    except RateLimitError as e:
        logger.error(f"Rate limit exceeded: {e}")
        raise

    except OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        raise

    except asyncio.TimeoutError as e:
        logger.error(f"Timeout occurred during summarization: {e}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error during summarization: {e}")
        raise