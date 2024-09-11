from apis.openai_summary_api import summarize_transcript
from config.config import OPENAI_CLIENT
from handlers.speech_handler import handle_speech_conversion
from utils.formatter import clean_markdown_symbols


async def handle_summary_request(update, context):
    """Handles summarization of the transcript."""
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="✅ Extracting key insights for you... 🎯")
    
    transcript = context.user_data.pop('transcript', None)
    user_language = update.effective_user.language_code if update.effective_user.language_code else 'en' # noqa: F841
    # Call the OpenAI API to summarize the transcript
    summary = await summarize_transcript(transcript, OPENAI_CLIENT, user_language)
    plain_text_summary = clean_markdown_symbols(summary)
  
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=plain_text_summary
        )
    # Store the summary in user data and pass to the speech handler
    context.user_data['summary'] = plain_text_summary

    await handle_speech_conversion(update, context)
