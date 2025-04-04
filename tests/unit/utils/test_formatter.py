from utils.formatter import extract_video_id, remove_markdown_v2_symbols

class TestFormatter:
    """Test class for formatter utility functions."""
    
    def test_extract_video_id_standard_url(self):
        """Test extracting video ID from a standard YouTube URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_extract_video_id_short_url(self):
        """Test extracting video ID from a YouTube short URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_extract_video_id_embed_url(self):
        """Test extracting video ID from a YouTube embed URL."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_extract_video_id_shorts_url(self):
        """Test extracting video ID from a YouTube Shorts URL."""
        url = "https://www.youtube.com/shorts/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_extract_video_id_invalid_url(self):
        """Test that None is returned for invalid URLs."""
        url = "https://example.com/not-a-youtube-url"
        assert extract_video_id(url) is None
    
    def test_remove_markdown_v2_symbols(self):
        """Test removing Markdown V2 symbols from text."""
        text = "This is a *bold* text with #hashtags and **double asterisks**"
        cleaned_text = remove_markdown_v2_symbols(text)
        assert cleaned_text == "This is a bold text with hashtags and double asterisks"
    
    def test_remove_markdown_v2_symbols_custom_symbols(self):
        """Test removing custom Markdown V2 symbols from text."""
        text = "This is a *bold* text with #hashtags and _underscores_"
        cleaned_text = remove_markdown_v2_symbols(text, symbols_to_remove=["_"])
        assert cleaned_text == "This is a *bold* text with #hashtags and underscores"