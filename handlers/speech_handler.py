# from apis.text_to_speech import convert_summary_to_speech
# from utils.logger import logger

# async def handle_speech_conversion(update, context):
#     """Handles converting the summary to speech and sending it to the user."""
#     summary = context.user_data.get('summary')
    
#     if summary:
#         audio_file = await convert_summary_to_speech(summary)
#         if audio_file:
#             await context.bot.send_audio(chat_id=update.message.chat_id, audio=audio_file)
#         else:
#             await update.message.reply_text("Error generating speech from summary.")
#     else:
#         await update.message.reply_text("No summary available for speech conversion.")