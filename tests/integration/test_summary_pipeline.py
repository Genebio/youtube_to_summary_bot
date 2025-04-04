import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from handlers.url_handler import handle_video_link
from apis.fetch_transcript import fetch_youtube_transcript
from apis.summary import summarize_transcript
from utils.formatter import extract_video_id
from utils.cache import get_cached_data, set_cached_data

class TestSummaryPipeline:
    """Integration tests for the complete YouTube summary pipeline."""
    
    @pytest.mark.asyncio
    @patch('handlers.url_handler.fetch_youtube_transcript')
    @patch('handlers.url_handler.summarize_transcript')
    @patch('handlers.url_handler.SummaryRepository')
    @patch('handlers.url_handler.SessionRepository')
    @patch('handlers.url_handler.UserRepository')
    @patch('handlers.url_handler.get_db')
    @patch('handlers.url_handler.init_db')
    async def test_complete_summary_pipeline(
        self, mock_init_db, mock_get_db, mock_user_repo, 
        mock_session_repo, mock_summary_repo, mock_summarize, 
        mock_fetch_transcript, mock_video_data, mock_transcript_data, 
        mock_summary_data, mock_telegram_update, mock_telegram_context
    ):
        """Test the complete flow from URL to summary."""
        # Set up mocks
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])
        
        # User repository mock
        mock_user = MagicMock()
        mock_user.user_id = 1
        mock_user_repo_instance = MagicMock()
        mock_user_repo_instance.get_or_create_user.return_value = mock_user
        mock_user_repo.return_value = mock_user_repo_instance
        
        # Session repository mock
        mock_session = MagicMock()
        mock_session.session_id = 1
        mock_session_repo_instance = MagicMock()
        mock_session_repo_instance.create_session.return_value = mock_session
        mock_session_repo_instance.end_session.return_value = mock_session
        mock_session_repo.return_value = mock_session_repo_instance
        
        # Summary repository mock (no existing summary)
        mock_summary_repo_instance = MagicMock()
        mock_summary_repo_instance.fetch_summary.return_value = None
        mock_summary_repo_instance.save_summary.return_value = MagicMock()
        mock_summary_repo.return_value = mock_summary_repo_instance
        
        # Transcript and summary mock
        mock_fetch_transcript.return_value = mock_transcript_data
        mock_summarize.return_value = mock_summary_data
        
        # Call the handler
        await handle_video_link(mock_telegram_update, mock_telegram_context)
        
        # Verify the pipeline was executed correctly
        mock_init_db.assert_called_once()
        mock_get_db.assert_called_once()
        mock_user_repo_instance.get_or_create_user.assert_called_once()
        mock_session_repo_instance.create_session.assert_called_once()
        mock_summary_repo_instance.fetch_summary.assert_called_once()
        mock_fetch_transcript.assert_called_once()
        mock_summarize.assert_called_once()
        mock_summary_repo_instance.save_summary.assert_called_once()
        mock_session_repo_instance.end_session.assert_called_once()
        
        # Verify the Telegram message responses
        assert mock_telegram_update.message.reply_text.call_count >= 3
    
    @pytest.mark.asyncio
    @patch('handlers.url_handler.fetch_youtube_transcript')
    @patch('handlers.url_handler.summarize_transcript')
    @patch('handlers.url_handler.SummaryRepository')
    @patch('handlers.url_handler.SessionRepository')
    @patch('handlers.url_handler.UserRepository')
    @patch('handlers.url_handler.get_db')
    @patch('handlers.url_handler.init_db')
    async def test_pipeline_with_existing_summary(
        self, mock_init_db, mock_get_db, mock_user_repo, 
        mock_session_repo, mock_summary_repo, mock_summarize, 
        mock_fetch_transcript, mock_video_data, mock_telegram_update, 
        mock_telegram_context
    ):
        """Test the flow when a summary already exists in the database."""
        # Set up mocks
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])
        
        # User and session repository mocks
        mock_user = MagicMock()
        mock_user.user_id = 1
        mock_user_repo_instance = MagicMock()
        mock_user_repo_instance.get_or_create_user.return_value = mock_user
        mock_user_repo.return_value = mock_user_repo_instance
        
        mock_session = MagicMock()
        mock_session.session_id = 1
        mock_session_repo_instance = MagicMock()
        mock_session_repo_instance.create_session.return_value = mock_session
        mock_session_repo_instance.end_session.return_value = mock_session
        mock_session_repo.return_value = mock_session_repo_instance
        
        # Summary repository mock (WITH existing summary)
        mock_summary_repo_instance = MagicMock()
        mock_summary_repo_instance.fetch_summary.return_value = "This is an existing summary from the database."
        mock_summary_repo.return_value = mock_summary_repo_instance
        
        # Call the handler
        await handle_video_link(mock_telegram_update, mock_telegram_context)
        
        # Verify that existing summary was used
        mock_init_db.assert_called_once()
        mock_get_db.assert_called_once()
        mock_user_repo_instance.get_or_create_user.assert_called_once()
        mock_session_repo_instance.create_session.assert_called_once()
        mock_summary_repo_instance.fetch_summary.assert_called_once()
        
        # Should not call these methods since summary exists
        mock_fetch_transcript.assert_not_called()
        mock_summarize.assert_not_called()
        mock_summary_repo_instance.save_summary.assert_not_called()
        
        # Session should be ended
        mock_session_repo_instance.end_session.assert_called_once()
        
        # Verify the Telegram message responses
        assert mock_telegram_update.message.reply_text.call_count >= 3
    
    @pytest.mark.asyncio
    @patch('handlers.url_handler.fetch_youtube_transcript')
    @patch('handlers.url_handler.SummaryRepository')
    @patch('handlers.url_handler.SessionRepository')
    @patch('handlers.url_handler.UserRepository')
    @patch('handlers.url_handler.get_db')
    @patch('handlers.url_handler.init_db')
    async def test_pipeline_with_no_transcript(
        self, mock_init_db, mock_get_db, mock_user_repo, 
        mock_session_repo, mock_summary_repo, mock_fetch_transcript, 
        mock_video_data, mock_telegram_update, mock_telegram_context
    ):
        """Test the flow when no transcript is found for the video."""
        # Set up mocks
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])
        
        # User and session repository mocks
        mock_user = MagicMock()
        mock_user.user_id = 1
        mock_user_repo_instance = MagicMock()
        mock_user_repo_instance.get_or_create_user.return_value = mock_user
        mock_user_repo.return_value = mock_user_repo_instance
        
        mock_session = MagicMock()
        mock_session.session_id = 1
        mock_session_repo_instance = MagicMock()
        mock_session_repo_instance.create_session.return_value = mock_session
        mock_session_repo_instance.end_session.return_value = mock_session
        mock_session_repo.return_value = mock_session_repo_instance
        
        # Summary repository mock (no existing summary)
        mock_summary_repo_instance = MagicMock()
        mock_summary_repo_instance.fetch_summary.return_value = None
        mock_summary_repo.return_value = mock_summary_repo_instance
        
        # Transcript mock (returns None to simulate no transcript found)
        mock_fetch_transcript.return_value = None
        
        # Call the handler
        await handle_video_link(mock_telegram_update, mock_telegram_context)
        
        # Verify pipeline was executed correctly
        mock_init_db.assert_called_once()
        mock_get_db.assert_called_once()
        mock_user_repo_instance.get_or_create_user.assert_called_once()
        mock_session_repo_instance.create_session.assert_called_once()
        mock_summary_repo_instance.fetch_summary.assert_called_once()
        mock_fetch_transcript.assert_called_once()
        
        # Should not try to summarize or save without a transcript
        mock_summary_repo_instance.save_summary.assert_not_called()
        
        # Session should be ended
        mock_session_repo_instance.end_session.assert_called_once_with(
            mock_session, end_reason="No transcript fetched"
        )
        
        # Verify error message was sent
        assert mock_telegram_update.message.reply_text.call_count >= 2