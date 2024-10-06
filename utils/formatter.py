import re
from typing import Optional
import tiktoken
from config.constants import VIDEO_ID_REGEX, MAX_TOKENS, OPENAI_SUMMARY_MODEL


def extract_video_id(url: str) -> Optional[str]:
    """
    Extracts the video ID from a variety of YouTube URL formats.
    """
    match = re.search(VIDEO_ID_REGEX, url)
    if match:
        return match.group(1)

def count_tokens(text):
    encoding = tiktoken.encoding_for_model(OPENAI_SUMMARY_MODEL)
    return len(encoding.encode(text))

def truncate_by_token_count(text):
    encoding = tiktoken.encoding_for_model(OPENAI_SUMMARY_MODEL)
    tokens = encoding.encode(text)
    truncated_tokens = tokens[:MAX_TOKENS]
    return encoding.decode(truncated_tokens)
