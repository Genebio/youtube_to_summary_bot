from apis.openai_api import summarize_transcript
from config.config import OPENAI_CLIENT
from utils.logger import logger #TODO

async def handle_summary_request(update, context):
    """Handles summarization of the transcript."""
    transcript = context.user_data.get('transcript')
    user_language = "en"  # Default to English, you can enhance this by detecting the user's locale.
    
    if transcript:
        await context.bot.send_message(chat_id=update.message.chat_id, text="Summarizing the transcript...")

        # Call the OpenAI API to summarize the transcript
        summary = await summarize_transcript(transcript, OPENAI_CLIENT, user_language)
        
        if "Error" in summary:
            await context.bot.send_message(chat_id=update.message.chat_id, text=summary)
        else:
            await context.bot.send_message(chat_id=update.message.chat_id, text=f"Summary:\n{summary}")
            # Store the summary in user data and pass to the speech handler
            context.user_data['summary'] = summary
            # await speech_handler.handle_speech_conversion(update, context) #TODO
    else:
        await update.message.reply_text("No transcript available to summarize.")