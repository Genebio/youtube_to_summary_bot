import re
import logging
from telegram.error import BadRequest
from telegram import Update
from telegram.ext import ContextTypes
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command."""
    await update.message.reply_text(
        text=(
            "*What can this bot do?*\n\n"
            "Get quick video summaries:\n\n"
            "1\\. Send a YouTube link\n"
            "2\\. Receive a concise summary\n"
            "3\\. Save time and grasp key insights fast\n\n"
            "💡 *Tip:* Perfect for quick research or deciding what to watch\\.\n\n"
            "🚀 *Ready? Drop a link to get started\\!*"
        ),
        parse_mode="MarkdownV2"
    )

def extract_video_id(url: str) -> str:
    """Extracts the video ID from a YouTube URL."""
    match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
    return match.group(1) if match else None

def fetch_transcript(video_id: str) -> str:
    """Fetches the transcript (manual or auto-generated) for a YouTube video."""
    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Prioritize manual transcripts over auto-generated ones
        transcript = next((t for t in transcripts if not t.is_generated), None)
        if not transcript:
            transcript = next((t for t in transcripts if t.is_generated), None)
        
        if transcript:
            return ' '.join([entry['text'] for entry in transcript.fetch()])
        return "No transcript found."
    
    except NoTranscriptFound:
        return "No transcript found for this video."
    except TranscriptsDisabled:
        return "Transcripts are disabled for this video."
    except VideoUnavailable:
        return "The video is unavailable."
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

def escape_markdown(text: str) -> str:
    """Escapes necessary special characters for Telegram MarkdownV2."""
    escape_chars = r'_*\[\]()~`>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)

def summarize_text(text: str, client: OpenAI, language: str = "en") -> str:
    """Summarizes the provided text using the OpenAI API and returns it in MarkdownV2 format, in the user's locale."""
    try:
        # Translate prompt to the user's language using the language variable
        completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"Summarize this video by highlighting the main points, key statements, and notable quotes from the speakers. "
                           f"Translate the summary to {language}. Ensure the summary includes core ideas and conclusions clearly:\n{text}"
            }],
            model="gpt-4o-mini"
        )
        # Get the summary and escape it for MarkdownV2
        summary = completion.choices[0].message.content
        return escape_markdown(summary)  # Ensure it's escaped properly for MarkdownV2
    except Exception as e:
        logger.error(f"Error during summarization: {e}")
        return escape_markdown(f"An error occurred while summarizing: {e}")

async def handle_video_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processes the YouTube video link provided by the user."""
    url = update.message.text
    
    # Extract the video ID from the URL
    video_id = extract_video_id(url)
    
    if not video_id:
        await update.message.reply_text("⚠️ Oops! That doesn't seem like a valid YouTube link. Please double-check and try again. 😊")
        return

    await update.message.reply_text("🔍 Fetching the transcript...")

    # Fetch the transcript
    transcript = fetch_transcript(video_id)
    
    if "No transcript found" in transcript or "disabled" in transcript or "unavailable" in transcript:
        await update.message.reply_text(transcript)
        return

    await update.message.reply_text("✅ Transcript ready! Summarizing the key points for you... 🎯")

    # Summarize the transcript based on the user's locale
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # Detect user's locale from the Telegram context (if available) or use 'en' as default
    user_locale = update.effective_user.language_code if update.effective_user.language_code else 'en'
    
    # Call summarize_text with locale
    summary = summarize_text(transcript, client, language=user_locale)

    # Handle potential errors in summary
    if "An error occurred" in summary:
        await update.message.reply_text(summary)
        return

    # Escape the summary for MarkdownV2 and send it
    await update.message.reply_text("🎉 Done! Here's your video summary: 👇")

    try:
        await update.message.reply_text(text=summary, parse_mode="MarkdownV2")
    except BadRequest as e:
        # Handle BadRequest exception (usually due to formatting errors)
        logger.error(f"BadRequest error while sending message: {e}")
        await update.message.reply_text("❗ There was an error formatting the summary. Please try again.")
    except Exception as e:
        # Log any other exceptions
        logger.error(f"Unexpected error: {e}")
        await update.message.reply_text("❗ An unexpected error occurred while sending the summary.")