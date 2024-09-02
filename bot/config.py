import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("No TOKEN found in environment variables.")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("No OPENAI_API_KEY found in environment variables.")