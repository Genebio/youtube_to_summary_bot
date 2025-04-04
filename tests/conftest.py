import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

@pytest.fixture
def mock_video_data():
    """Sample video data for testing."""
    return {
        "video_id": "dQw4w9WgXcQ",  # Rick Astley's "Never Gonna Give You Up"
        "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "language_code": "en",
    }

@pytest.fixture
def mock_transcript_data():
    """Sample transcript data for testing."""
    return {
        "transcript_text": "This is a sample transcript for testing. It contains some text that can be summarized.",
        "video_duration": 213  # Duration in seconds
    }

@pytest.fixture
def mock_summary_data():
    """Sample summary data for testing."""
    return {
        "summary": "This is a sample summary of the transcript.",
        "input_tokens": 25,
        "output_tokens": 10,
        "error": None
    }

@pytest.fixture
def mock_redis_client():
    """Mocked Redis client."""
    client = AsyncMock()
    client.get.return_value = None
    client.setex.return_value = True
    client.ping.return_value = True
    return client

@pytest.fixture
def mock_db_session():
    """Mocked SQLAlchemy session."""
    session = MagicMock()
    session.query.return_value.filter.return_value.first.return_value = None
    session.commit.return_value = None
    session.add.return_value = None
    session.refresh.return_value = None
    return session

@pytest.fixture
def mock_openai_client():
    """Mocked OpenAI client."""
    client = AsyncMock()
    completion_mock = AsyncMock()
    completion_mock.choices = [MagicMock(message=MagicMock(content="This is a sample summary."))]
    completion_mock.usage = MagicMock(prompt_tokens=25, completion_tokens=10)
    client.chat.completions.create.return_value = completion_mock
    return client

@pytest.fixture
def mock_telegram_update():
    """Mocked Telegram update object."""
    update = MagicMock()
    update.effective_user = MagicMock(
        language_code="en",
        id=12345,
        username="test_user"
    )
    update.message = MagicMock(
        text="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        from_user=MagicMock(
            username="test_user",
            first_name="Test",
            last_name="User",
        ),
        reply_text=AsyncMock()
    )
    return update

@pytest.fixture
def mock_telegram_context():
    """Mocked Telegram context object."""
    return MagicMock()

# Async event loop for tests
@pytest.fixture
def event_loop():
    """Create an asyncio event loop for tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()