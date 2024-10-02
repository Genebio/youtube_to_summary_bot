from repositories.summary_repository import SummaryRepository
from repositories.user_repository import UserRepository
from apis.youtube_transcript_api import fetch_youtube_transcript
from apis.openai_summary_api import summarize_transcript
from apis.openai_text_to_speech_api import convert_summary_to_speech
from config.config import OPENAI_CLIENT
from utils.formatter import extract_video_id, ServiceResponse


class SummaryService:
    def __init__(self, db):
        self.summary_repo = SummaryRepository(db)
        self.user_repo = UserRepository(db)
        # SessionRepo will be added later
        # self.session_repo = SessionRepository(db)

    async def process_summary(self, video_url: str, user_id: int) -> ServiceResponse:
        """Handles the main logic for fetching the transcript and summarizing it."""
        
        # Step 1: Extract video_id from video_url
        video_id_response = extract_video_id(video_url)
        if not video_id_response.is_success():
            return ServiceResponse(error=video_id_response.error)
        video_id = video_id_response.data

        # Step 2: Fetch the user
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            return ServiceResponse(error="User not found")

        # Step 3: Fetch the language code for the user
        language_code = user.language_code
        if not language_code:
            return ServiceResponse(error="Language code not set for user")

        # Step 4: Fetch the transcript from YouTube
        transcript_response = await fetch_youtube_transcript(video_id)
        if not transcript_response.is_success():
            return ServiceResponse(error=transcript_response.error)
        transcript = transcript_response.data

        # Step 5: Summarize the transcript using OpenAI API
        summary_response = await summarize_transcript(transcript, OPENAI_CLIENT, language_code)
        if not summary_response.is_success():
            return ServiceResponse(error=summary_response.error)
        summary_text, input_tokens, output_tokens, summary_model = summary_response.data

        # Step 6: Session handling is deferred to SessionRepository (not implemented)
        session = None  # Placeholder until SessionRepository is implemented

        # Step 7: Save the new summary into the database using relationships
        new_summary = self.summary_repo.create_summary(
            user=user,  # Pass the User object
            session=session,  # SessionRepo will handle this once implemented
            video_url=video_url,
            video_id=video_id,
            language_code=language_code,
            text_summary=summary_text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            summary_model=summary_model
        )

        return ServiceResponse(data=new_summary)

    async def process_summary_to_audio(self, summary_id: int, summary_text: str) -> ServiceResponse:
        """Handles the optional TTS conversion of a summary to audio."""
        
        # Step 1: Convert the summary to audio using OpenAI TTS API
        tts_response = await convert_summary_to_speech(summary_text, OPENAI_CLIENT)
        if not tts_response.is_success():
            return ServiceResponse(error=tts_response.error)
        
        tts_data = tts_response.data

        # Step 2: Update the existing summary with TTS information
        updated_summary = self.summary_repo.update_summary_with_tts(
            summary_id=summary_id,
            requested_audio=True,
            got_audio=True,
            tts_model=tts_data['tts_model'],
            tts_tokens=tts_data['tts_tokens']
        )

        if updated_summary is None:
            return ServiceResponse(error="Failed to update summary with TTS data")

        return ServiceResponse(data=updated_summary)