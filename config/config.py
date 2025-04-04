import os
from google.cloud import secretmanager
from openai import AsyncOpenAI
import urllib.parse


def get_secret(secret_id, version_id, default=None):
    """Get a secret from Google Secret Manager or from environment variables with fallback to default."""
    # First try environment variables
    env_value = os.environ.get(secret_id)
    if env_value:
        return env_value
    
    # Then try Google Secret Manager
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/145075164540/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(name=name)
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        if default is not None:
            return default
        raise ValueError(f"Could not retrieve secret {secret_id}: {str(e)}")

# Telegram Bot Configuration
TOKEN = get_secret("TOKEN", "2")
if not TOKEN:
    raise ValueError("No TOKEN found in environment variables or Secret Manager.")

# OpenAI Configuration
OPENAI_API_KEY = get_secret("OPENAI_API_KEY", "1")
if not OPENAI_API_KEY:
    raise ValueError("No OPENAI_API_KEY found in environment variables or Secret Manager.")

# Database Configuration
DB_USER = get_secret("DB_USER", "2")
if not DB_USER:
    raise ValueError("No DB_USER found in environment variables or Secret Manager.")

DB_PASS = urllib.parse.quote(get_secret("DB_PASS", "2"))
if not DB_PASS:
    raise ValueError("No DB_PASS found in environment variables or Secret Manager.")

DB_NAME = get_secret("DB_NAME", "2")
if not DB_NAME:
    raise ValueError("No DB_NAME found in environment variables or Secret Manager.")

DB_HOST = get_secret("DB_HOST", "4")
if not DB_HOST:
    raise ValueError("No DB_HOST found in environment variables or Secret Manager.")

# Redis Configuration
REDIS_URL = get_secret("REDIS_URL", "1", default="redis://localhost:6379/0")
CACHE_EXPIRY_SECONDS = int(get_secret("CACHE_EXPIRY_SECONDS", "1", default="86400"))  # Default: 24 hours

# Rate Limiting Configuration
RATE_LIMIT_REQUESTS = int(get_secret("RATE_LIMIT_REQUESTS", "1", default="5"))
RATE_LIMIT_PERIOD = int(get_secret("RATE_LIMIT_PERIOD", "1", default="60"))  # seconds

# Initialize OpenAI client
OPENAI_CLIENT = AsyncOpenAI(api_key=OPENAI_API_KEY)

