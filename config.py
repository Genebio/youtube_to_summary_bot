from google.cloud import secretmanager

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