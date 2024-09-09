/app/
│
├── /apis/                  # All external API integrations
│   ├── youtube_api.py       # Handles YouTube transcript fetching logic
│   ├── openai_api.py        # Summarizes transcript using OpenAI API
│   └── text_to_speech.py    # Converts summaries to speech using an appropriate API
│
├── /handlers/               # Telegram bot handlers
│   ├── youtube_handler.py   # Manages YouTube-related commands
│   ├── summary_handler.py   # Handles transcript summarization
│   ├── speech_handler.py    # Handles summary to speech conversion
│   └── command_menu.py      # Manages bot commands like feedback and subscription
│
├── /utils/                  # Utilities and helpers
│   ├── logger.py            # Centralized logger setup
│   ├── formatter.py         # Formats messages for user interaction
│   └── localizer.py         # Localization handling (for multilingual support)
│
├── /config/                 # Configuration management
│   ├── config.py            # Stores secrets
│   ├── constants.py         # API prompts, button texts, other static constants
│   └── settings.py          # Global app settings (timeout, retry logic, etc.)
│
├── main.py                  # FastAPI app, initializes handlers and webhook
└── Dockerfile               # Containerization details for Cloud Run