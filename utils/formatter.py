import re
from typing import Optional, List
import tiktoken
from config.summary_config import SummaryConfig


def extract_video_id(url: str) -> Optional[str]:
    """
    Extracts the video ID from a variety of YouTube URL formats.
    """
    VIDEO_ID_REGEX = (
        r'(?:https?://)?'  # Match the protocol (http or https) (optional)
        r'(?:www\.)?'  # Optional www subdomain
        r'(?:youtube\.com|youtu\.be|youtube-nocookie\.com)'
        r'(?:.*[?&]v=|/embed/|/v/|/e/|/shorts/|/live/|/attribution_link?.*v=|/oembed\?url=.*v=|/)?' 
        r'([a-zA-Z0-9_-]{11})'  # Capture the 11-character video ID
    )
    match = re.search(VIDEO_ID_REGEX, url)
    if match:
        return match.group(1)

def count_tokens(text):
    encoding = tiktoken.encoding_for_model(SummaryConfig.get_model())
    return len(encoding.encode(text))

def truncate_by_token_count(text):
    encoding = tiktoken.encoding_for_model(SummaryConfig.get_model())
    tokens = encoding.encode(text)
    truncated_tokens = tokens[:SummaryConfig.get_max_tokens()]
    return encoding.decode(truncated_tokens)

def remove_markdown_v2_symbols(text: str, symbols_to_remove: List[str] = None) -> str:
    """
    Removes specified Markdown V2 symbols from the given text.
    """
    if symbols_to_remove is None:
        symbols_to_remove = ['*', '#']
    
    # Escape special regex characters
    escaped_symbols = [re.escape(symbol) for symbol in symbols_to_remove]
    
    # Create a pattern that matches any of the symbols
    pattern = '|'.join(escaped_symbols)
    
    # Remove the symbols
    cleaned_text = re.sub(pattern, '', text)
    
    return cleaned_text