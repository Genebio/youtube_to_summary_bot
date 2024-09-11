import tiktoken
from config.constants import MAX_TOKENS, OPENAI_SUMMARY_MODEL


def clean_markdown_symbols(summary: str) -> str:
    """
    Removes specified Markdown V2 symbols (e.g., '*', '#') from the summary.
    
    Args:
        summary (str): The summary text to clean.

    Returns:
        str: The cleaned summary.
    """
    # Dictionary of Markdown V2 symbols to remove
    remove_chars = {'*': '', '#': ''}
    
    # Create a translation table from the dictionary
    translation_table = str.maketrans(remove_chars)
    
    # Translate the summary using the translation table
    return summary.translate(translation_table)

def count_tokens(text):
    encoding = tiktoken.encoding_for_model(OPENAI_SUMMARY_MODEL)
    return len(encoding.encode(text))

def truncate_by_token_count(text):
    encoding = tiktoken.encoding_for_model(OPENAI_SUMMARY_MODEL)
    tokens = encoding.encode(text)
    truncated_tokens = tokens[:MAX_TOKENS]
    return encoding.decode(truncated_tokens)
