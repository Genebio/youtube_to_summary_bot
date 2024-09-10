from apis.openai_api import summarize_transcript
from config.config import OPENAI_CLIENT


async def handle_summary_request(update, context, transcript):
    """Handles summarization of the transcript."""
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="✨ Extracting key insights for you... 💡")
    
    user_language = update.effective_user.get("language_code", "en")
    # Call the OpenAI API to summarize the transcript
    summary = await summarize_transcript(transcript, OPENAI_CLIENT, user_language)

    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="🎉 Done! Here's your video summary: 👇")  
    await context.bot.send_message(chat_id=update.message.chat_id, text=summary)
    # Store the summary in user data and pass to the speech handler
    # context.user_data['summary'] = summary

    # await speech_handler.handle_speech_conversion(update, context) #TODO
