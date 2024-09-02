import re
import logging
from telegram import Update
from telegram.ext import ContextTypes
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from bot.config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text("Hi! Send me a YouTube video link, and I'll summarize it for you!")

def extract_video_id(url: str) -> str:
    """Extracts the video ID from a YouTube URL."""
    match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
    return match.group(1) if match else None

def get_youtube_transcript(video_id: str) -> str:
    """Fetches the first available auto-generated transcript of a YouTube video."""
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        for transcript in transcript_list:
            if transcript.is_generated:
                transcript_text = ' '.join([entry['text'] for entry in transcript.fetch()])
                return transcript_text
        return None
    except NoTranscriptFound:
        return None

def summarize_text(text: str, client: OpenAI) -> str:
    """Summarizes the provided text using the OpenAI API."""
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content":
             f"Summarize the video by providing a detailed description of the key points discussed. Include any important statements or quotes made by the speakers, as well as the reasoning or explanations they provide for their arguments. Ensure that the summary captures the main ideas and conclusions presented in the video.\n{text}"}
        ],
        model="gpt-4o-mini"
    )
    
    summary = chat_completion.choices[0].message.content
    return summary

async def handle_video_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the received YouTube video link."""
    url = update.message.text
    video_id = extract_video_id(url)
    
    if not video_id:
        await update.message.reply_text("Invalid YouTube URL provided.")
        return
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    transcript_text = get_youtube_transcript(video_id)
    
    if transcript_text:
        summary = summarize_text(transcript_text, client)
        try:
            await update.message.reply_text("Summary of the video transcript:")
            await update.message.reply_text(summary)
        except telegram.error.Forbidden:
            logger.error(f"Failed to send message to user {update.message.chat_id}: Bot was blocked.")
    else:
        await update.message.reply_text("No auto-generated transcript found for the provided video.")