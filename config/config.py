from google.cloud import secretmanager
from openai import AsyncOpenAI
import urllib.parse
from utils.logger import logger


def get_secret(secret_id, version_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/145075164540/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")

TOKEN = get_secret("TOKEN", "2")
if not TOKEN:
    raise ValueError("No TOKEN found in environment variables.")

OPENAI_API_KEY = get_secret("OPENAI_API_KEY", "1")
if not OPENAI_API_KEY:
    raise ValueError("No OPENAI_API_KEY found in environment variables.")

DB_USER = get_secret("DB_USER", "2")
logger.info(f"DB_USER: {DB_USER}")
if not DB_USER:
    raise ValueError("No DB_USER found in environment variables.")

DB_PASS = urllib.parse.quote(get_secret("DB_PASS", "2"))
logger.info(f"DB_PASS: {DB_PASS}")
if not DB_PASS:
    raise ValueError("No DB_PASS found in environment variables.")

DB_NAME = get_secret("DB_NAME", "2")
logger.info(f"DB_NAME: {DB_NAME}")
if not DB_NAME:
    raise ValueError("No DB_NAME found in environment variables.")

DB_HOST = get_secret("DB_HOST", "4")
logger.info(f"DB_HOST: {DB_HOST}")
if not DB_HOST:
    raise ValueError("No DB_HOST found in environment variables.")


OPENAI_CLIENT = AsyncOpenAI(api_key=OPENAI_API_KEY)

