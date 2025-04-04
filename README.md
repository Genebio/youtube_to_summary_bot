# YouTube Summary Bot

A Telegram bot that summarizes YouTube videos by fetching their transcripts and using OpenAI to generate concise, informative summaries.

## Features

- Fetches transcripts from YouTube videos
- Generates concise summaries using OpenAI's GPT models
- Stores summaries in a database for quick retrieval
- Supports multiple languages
- Implements rate limiting to prevent abuse
- Uses Redis caching to improve performance and reduce API costs
- Comprehensive test suite for reliability

## Architecture

```
/apis/                  # External API integrations
    /fetch_transcript.py       # YouTube transcript fetching
    /summary.py               # OpenAI summarization
    /tts.py                   # Text-to-speech conversion

/handlers/               # Telegram bot handlers
    /url_handler.py            # Processes YouTube links
    /command_menu.py           # Handles bot commands

/models/                 # SQLAlchemy models
    /user_model.py             # User data
    /session_model.py          # Session tracking
    /summary_model.py          # Stored summaries

/repositories/           # Database interactions
    /user_repository.py        # User data storage
    /session_repository.py     # Session tracking
    /summary_repository.py     # Summary storage

/utils/                  # Helper utilities
    /cache.py                  # Redis caching
    /formatter.py              # Text formatting
    /rate_limiter.py           # Rate limiting
    /db_connection.py          # Database connection
    /logger.py                 # Logging configuration

/config/                 # Configuration
    /config.py                 # Environment variables and secrets
    /summary_config.py         # Summary generation parameters

/tests/                  # Test suite
    /unit/                     # Unit tests
    /integration/              # Integration tests
    /conftest.py               # Test fixtures
```

## Setup and Installation

### Prerequisites

- Python 3.11+
- PostgreSQL database
- Redis server (optional, for caching)
- Google Cloud Secret Manager (optional, for production)

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/Genebio/youtube_to_summary_bot
   cd youtube_to_summary
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file with the following variables:
   ```
   TOKEN=your_telegram_bot_token
   OPENAI_API_KEY=your_openai_api_key
   DB_USER=postgres_user
   DB_PASS=postgres_password
   DB_NAME=youtube_summary
   DB_HOST=localhost
   REDIS_URL=redis://localhost:6379/0
   ```

5. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit

# Run integration tests only
pytest tests/integration

# Run with coverage report
pytest --cov=. --cov-report=term
```

## Deployment

### Docker

Build and run the Docker container:
```bash
docker build -t youtube-summary-bot .
docker run -p 8080:8080 youtube-summary-bot
```

### Google Cloud Run

1. Build the container:
   ```bash
   gcloud builds submit --tag gcr.io/your-project-id/youtube-summary-bot
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy youtube-summary-bot \
     --image gcr.io/your-project-id/youtube-summary-bot \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

## API Documentation

After starting the server, visit:
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.