import pytest
from unittest.mock import patch, MagicMock
from youtube_transcript_api import (
    NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
)
from apis.fetch_transcript import fetch_youtube_transcript

class TestFetchTranscript:
    """Test class for YouTube transcript fetching functionality."""
    
    @pytest.mark.asyncio
    @patch('apis.fetch_transcript.asyncio.to_thread')
    async def test_fetch_transcript_success_manual(self, mock_to_thread):
        """Test successful fetching of a manual transcript."""
        # Mock the transcript API response
        mock_transcript = MagicMock()
        mock_transcript.is_generated = False
        mock_transcript.fetch.return_value = [
            {"text": "This is", "start": 0.0, "duration": 1.0},
            {"text": "a test transcript", "start": 1.0, "duration": 2.0}
        ]
        
        mock_transcripts = MagicMock()
        mock_transcripts.__iter__.return_value = [mock_transcript]
        
        # Set up the asyncio.to_thread mock
        mock_to_thread.return_value = mock_transcripts
        
        # Call the function
        result = await fetch_youtube_transcript("test_video_id")
        
        # Verify results
        assert result is not None
        assert result["transcript_text"] == "This is a test transcript"
        assert result["video_duration"] == 3.0  # 1.0 + 2.0
        mock_to_thread.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('apis.fetch_transcript.asyncio.to_thread')
    async def test_fetch_transcript_success_auto_generated(self, mock_to_thread):
        """Test successful fetching of an auto-generated transcript."""
        # Mock the first transcript (which is NOT manual)
        mock_transcript1 = MagicMock()
        mock_transcript1.is_generated = True
        mock_transcript1.fetch.return_value = [
            {"text": "This is", "start": 0.0, "duration": 1.0},
            {"text": "an auto-generated transcript", "start": 1.0, "duration": 2.0}
        ]
        
        mock_transcripts = MagicMock()
        mock_transcripts.__iter__.return_value = [mock_transcript1]
        
        # Set up the asyncio.to_thread mock
        mock_to_thread.return_value = mock_transcripts
        
        # Call the function
        result = await fetch_youtube_transcript("test_video_id")
        
        # Verify results
        assert result is not None
        assert result["transcript_text"] == "This is an auto-generated transcript"
        assert result["video_duration"] == 3.0  # 1.0 + 2.0
        mock_to_thread.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('apis.fetch_transcript.asyncio.to_thread')
    async def test_fetch_transcript_no_transcript_found(self, mock_to_thread):
        """Test handling of NoTranscriptFound exception."""
        mock_to_thread.side_effect = NoTranscriptFound("No transcript found")
        
        result = await fetch_youtube_transcript("test_video_id")
        
        assert result is None
        mock_to_thread.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('apis.fetch_transcript.asyncio.to_thread')
    async def test_fetch_transcript_transcripts_disabled(self, mock_to_thread):
        """Test handling of TranscriptsDisabled exception."""
        mock_to_thread.side_effect = TranscriptsDisabled("Transcripts disabled")
        
        result = await fetch_youtube_transcript("test_video_id")
        
        assert result is None
        mock_to_thread.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('apis.fetch_transcript.asyncio.to_thread')
    async def test_fetch_transcript_video_unavailable(self, mock_to_thread):
        """Test handling of VideoUnavailable exception."""
        mock_to_thread.side_effect = VideoUnavailable("Video unavailable")
        
        result = await fetch_youtube_transcript("test_video_id")
        
        assert result is None
        mock_to_thread.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('apis.fetch_transcript.asyncio.to_thread')
    async def test_fetch_transcript_empty_transcript_data(self, mock_to_thread):
        """Test handling of empty transcript data."""
        mock_transcript = MagicMock()
        mock_transcript.is_generated = False
        mock_transcript.fetch.return_value = []
        
        mock_transcripts = MagicMock()
        mock_transcripts.__iter__.return_value = [mock_transcript]
        
        mock_to_thread.return_value = mock_transcripts
        
        result = await fetch_youtube_transcript("test_video_id")
        
        assert result is None
        mock_to_thread.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('apis.fetch_transcript.asyncio.to_thread')
    @patch('apis.fetch_transcript.get_cached_data')
    @patch('apis.fetch_transcript.set_cached_data')
    async def test_fetch_transcript_with_cache(self, mock_set_cached, mock_get_cached, mock_to_thread):
        """Test cache integration with transcript fetching."""
        # First test a cache miss
        mock_get_cached.return_value = None
        
        mock_transcript = MagicMock()
        mock_transcript.is_generated = False
        mock_transcript.fetch.return_value = [
            {"text": "This is", "start": 0.0, "duration": 1.0},
            {"text": "a test transcript", "start": 1.0, "duration": 2.0}
        ]
        
        mock_transcripts = MagicMock()
        mock_transcripts.__iter__.return_value = [mock_transcript]
        
        mock_to_thread.return_value = mock_transcripts
        
        result = await fetch_youtube_transcript("test_video_id")
        
        assert result is not None
        assert result["transcript_text"] == "This is a test transcript"
        mock_get_cached.assert_called_once()
        mock_set_cached.assert_called_once()
        
        # Reset mocks for cache hit test
        mock_get_cached.reset_mock()
        mock_set_cached.reset_mock()
        mock_to_thread.reset_mock()
        
        # Now test a cache hit
        cached_data = {
            "transcript_text": "This is a cached transcript",
            "video_duration": 5.0
        }
        mock_get_cached.return_value = cached_data
        
        result = await fetch_youtube_transcript("test_video_id")
        
        assert result is not None
        assert result == cached_data
        mock_get_cached.assert_called_once()
        mock_set_cached.assert_not_called()
        mock_to_thread.assert_not_called()