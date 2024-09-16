/app/
│
├── /apis/                  # All external API integrations
│   ├── youtube_transcript_api.py       # Handles YouTube transcript fetching logic
│   ├── openai_summary_api.py           # Summarizes transcript using OpenAI API
│   └── openai_text_to_speech_api.py    # Converts summaries to speech using an appropriate API
│
├── /handlers/               # Telegram bot handlers
│   ├── transcript_handler.py           # Manages YouTube-related commands
│   ├── summary_handler.py              # Handles transcript summarization
│   ├── speech_handler.py               # Handles summary to speech conversion
│   └── command_menu.py                 # Manages bot commands like feedback and subscription
│
├── /services/               # Business logic layer
│   ├── user_service.py                   # Handles user data processing
│   ├── session_service.py                # Manages user session tracking
│   ├── subscription_status_service.py    # Tracks subscription status changes
│   └── summary_service.py                # Orchestrates transcript summarization
│
├── /repositories/           # Database interactions layer
│   ├── user_repository.py                # Handles user-related database queries
│   ├── session_repository.py             # Manages session data persistence
│   ├── summary_repository.py             # Manages summaries storage in DB
│   └── subscription_repository.py        # Manages subscription tracking in DB
│
├── /models/                 # SQLAlchemy models
│   ├── user_model.py                    # User model
│   ├── session_model.py                 # Session model
│   ├── summary_model.py                 # Summary model
│   └── subscription_status_model.py     # Subscription status model
│
├── /utils/                  # Utilities and helpers
│   ├── logger.py                        # Centralized logger setup
│   ├── formatter.py                     # Formats messages for user interaction
│   ├── localizer.py                     # Localization handling (for multilingual support)
│   └── db_connection.py                 # Database connection and session handling
│
├── /config/                 # Configuration management
│   ├── config.py                       # Stores secrets and environment-specific variables
│   ├── constants.py                    # API prompts, button texts, other static constants
│   ├── settings.py                     # Global app settings (timeout, retry logic, etc.)
│   └── locales.py                      # Actual locale translations
│
├── main.py                  # FastAPI app, initializes handlers and webhook
└── Dockerfile               # Containerization details for Cloud Run


# Explanation

1. /services/ Directory:

	•	This directory contains business logic. The services are responsible for coordinating multiple actions, processing data, and interacting with repositories and external APIs.
	•	Each service focuses on a specific aspect of your application. For example:
	•	user_service.py: Handles all user-related logic (e.g., user creation, updating).
	•	session_service.py: Tracks user session data and manages when a session starts or ends.
	•	subscription_service.py: Manages subscription status changes and billing logic.
	•	summary_service.py: Coordinates transcript fetching, summarization, and TTS processing.

Benefit: Separating the logic layer makes it easy to manage and test.

2. /repositories/ Directory:

	•	The repository layer abstracts database interaction (CRUD operations). Instead of having SQL queries spread across different parts of the app, it’s centralized here.
	•	Each repository is tied to a specific table or entity in the database. For example:
	•	user_repository.py: Performs queries for users table (e.g., fetching, updating users).
	•	session_repository.py: Handles session persistence and queries.
	•	summary_repository.py: Handles summaries storage and retrieval.
	•	subscription_repository.py: Manages subscription status and history.

Benefit: This keeps database queries separate from business logic, making the code more modular and easier to maintain.

3. /models/ Directory:

	•	Contains the SQLAlchemy models for your database entities. You already have the database structure designed for users, sessions, summaries, and subscription statuses.
	•	Each model is a representation of a table in your database, for example:
	•	user_model.py: Defines the structure of the users table.
	•	session_model.py: Defines the structure of the sessions table.
	•	summary_model.py: Defines the structure of the summaries table.
	•	subscription_model.py: Defines the structure of the subscription_status table.

Benefit: Keeps your data models organized and distinct from logic and queries.

4. /utils/db_connection.py:

	•	Contains reusable database connection logic. You can place your SQLAlchemy engine and session management here, ensuring that the database connection is consistent across your app.