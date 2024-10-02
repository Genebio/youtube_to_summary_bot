import re
import tiktoken
from config.constants import VIDEO_ID_REGEX, MAX_TOKENS, OPENAI_SUMMARY_MODEL


class ServiceResponse:
    def __init__(self, data=None, error=None):
        self.data = data
        self.error = error

    def is_success(self):
        """Returns True if the response has data and no error."""
        return self.data is not None and self.error is None


def extract_video_id(url: str) -> ServiceResponse:
    """
    Extracts the video ID from a variety of YouTube URL formats.
    """
    match = re.search(VIDEO_ID_REGEX, url)
    
    if match:
        video_id = match.group(1)
        return ServiceResponse(data=video_id)
    return ServiceResponse(error="Unable to extract video ID.")

def count_tokens(text):
    encoding = tiktoken.encoding_for_model(OPENAI_SUMMARY_MODEL)
    return len(encoding.encode(text))

def truncate_by_token_count(text):
    encoding = tiktoken.encoding_for_model(OPENAI_SUMMARY_MODEL)
    tokens = encoding.encode(text)
    truncated_tokens = tokens[:MAX_TOKENS]
    return encoding.decode(truncated_tokens)
