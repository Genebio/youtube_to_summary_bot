import re
from typing import Optional, List
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

def remove_markdown_v2_symbols(text: str, symbols_to_remove: List[str] = None) -> str:
    """
    Removes specified Markdown V2 symbols from the given text.
    If no symbols are specified, it removes '*' and '#' by default.

    Args:
    text (str): The input text containing Markdown V2 symbols.
    symbols_to_remove (List[str], optional): List of symbols to remove. Defaults to ['*', '#'].

    Returns:
    str: The text with specified Markdown V2 symbols removed.
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