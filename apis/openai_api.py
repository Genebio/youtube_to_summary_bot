import asyncio
from utils.logger import logger
from config.constants import OPENAI_SUMMARY_PROMPT


async def summarize_transcript(transcript: str, client, language: str = "en") -> str:
    """Summarizes the provided text using the OpenAI API and returns it in the user's locale."""
    try:
        # Make the API call asynchronously
        completion = await asyncio.to_thread(
            client.chat.completions.create, 
            messages=[{
                "role": "user",
                "content": f"{OPENAI_SUMMARY_PROMPT}{language}:\n{transcript}"
            }],
            model="gpt-4o-mini"
        )
        summary = completion.choices[0].message.content
        return summary
    except Exception as e:
        logger.error(f"Error during summarization: {e}")
        return f"An error occurred while summarizing: {e}"