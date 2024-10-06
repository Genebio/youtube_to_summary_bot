import asyncio
from typing import Dict, Optional
from openai import RateLimitError, OpenAIError
from utils.logger import logger
from config.summary_config import SummaryConfig
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((RateLimitError, OpenAIError, asyncio.TimeoutError)),
    reraise=True
)
async def summarize_transcript(transcript: str, client, language: str = "en") -> Dict[str, Optional[str | int]]:
    """Summarizes the provided text using the OpenAI API asynchronously, with retry logic."""
    try:
        logger.info("Attempting to summarize the transcript using OpenAI API...")

        completion = await client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"{SummaryConfig.get_prompt()}. Present the summary in '{language}' language:\n\n{transcript}"
            }],
            model=SummaryConfig.get_model()
        )

        summary = completion.choices[0].message.content
        input_tokens = completion.usage.prompt_tokens
        output_tokens = completion.usage.completion_tokens

        logger.info(f"Successfully generated summary. Input tokens: {input_tokens}, Output tokens: {output_tokens}")

        return {
            'summary': summary,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'error': None
        }

    except RateLimitError as e:
        logger.warning(f"Rate limit exceeded, retrying: {e}")
        raise  # This will be caught by Tenacity and retried

    except OpenAIError as e:
        logger.warning(f"OpenAI API error, retrying: {e}")
        raise  # This will be caught by Tenacity and retried

    except asyncio.TimeoutError as e:
        logger.warning(f"Timeout occurred during summarization, retrying: {e}")
        raise  # This will be caught by Tenacity and retried

    except Exception as e:
        logger.error(f"Unexpected error during summarization: {e}")
        return {'error': 'unexpected_error', 'details': str(e)}