import asyncio
from openai import RateLimitError, OpenAIError
from utils.logger import logger
from utils.formatter import ServiceResponse
from config.constants import OPENAI_SUMMARY_PROMPT, OPENAI_SUMMARY_MODEL


async def summarize_transcript(transcript: str, client, language: str = "en") -> ServiceResponse:
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
        input_tokens = completion.usage['prompt_tokens']
        output_tokens = completion.usage['completion_tokens']
        summary_model = OPENAI_SUMMARY_MODEL

        return ServiceResponse(data=(summary, input_tokens, output_tokens, summary_model))

    except RateLimitError as e:
        logger.error(f"Rate limit exceeded: {e}")
        return ServiceResponse(error=f"Rate limit exceeded: {str(e)}")

    except OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        return ServiceResponse(error=f"OpenAI API error: {str(e)}")

    except asyncio.TimeoutError as e:
        logger.error(f"Timeout occurred during summarization: {e}")
        return ServiceResponse(error=f"Timeout error: {str(e)}")

    except Exception as e:
        logger.error(f"Unexpected error during summarization: {e}")
        return ServiceResponse(error=f"Unexpected error: {str(e)}")