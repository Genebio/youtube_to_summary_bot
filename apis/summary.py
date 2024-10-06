import asyncio
from typing import Dict
from openai import RateLimitError, OpenAIError
from utils.logger import logger
from config.constants import OPENAI_SUMMARY_PROMPT, OPENAI_SUMMARY_MODEL


async def summarize_transcript(transcript: str, client, language: str = "en") -> Dict:
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

        # Extract summary from OpenAI API response
        summary = completion.choices[0].message.content
        input_tokens = completion.usage['prompt_tokens']
        output_tokens = completion.usage['completion_tokens']
        summary_model = OPENAI_SUMMARY_MODEL

        return {'summary': summary, 'summary_model': summary_model,
                'input_tokens': input_tokens, 'output_tokens': output_tokens}

    except RateLimitError as e:
        logger.error(f"Rate limit exceeded: {e}")
        return

    except OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        return

    except asyncio.TimeoutError as e:
        logger.error(f"Timeout occurred during summarization: {e}")
        return

    except Exception as e:
        logger.error(f"Unexpected error during summarization: {e}")
        return