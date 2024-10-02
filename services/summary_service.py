from repositories.summary_repository import SummaryRepository
from apis.fetch_transcript import fetch_youtube_transcript
from apis.summary import summarize_transcript
from apis.tts import convert_summary_to_speech
from config.config import OPENAI_CLIENT
from utils.formatter import extract_video_id, ServiceResponse
from models.user_model import User
from models.session_model import Session as UserSession

class SummaryService:
    def __init__(self, db):
        self.summary_repo = SummaryRepository(db)
        self.db = db  # Keep the database session for querying related objects

    async def process_summary(self, video_url: str, language_code: str, user_id: int, session_id: int) -> ServiceResponse:
        """Handles the main logic for fetching the transcript and summarizing it."""
        
        # Step 1: Extract video_id from video_url
        video_id_response = extract_video_id(video_url)
        if not video_id_response.is_success():
            return ServiceResponse(error=video_id_response.error)
        video_id = video_id_response.data

        # Step 2: Check if a summary already exists for this video and language
        existing_summary = self.summary_repo.get_summary_by_video_and_language(video_id, language_code)
        if existing_summary:
            return ServiceResponse(data=existing_summary)

        # Step 3: Fetch the User and Session objects based on the provided IDs
        user = self.db.query(User).filter_by(user_id=user_id).first()
        session = self.db.query(UserSession).filter_by(session_id=session_id).first()

        if not user or not session:
            return ServiceResponse(error="Invalid user or session.")

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

        # Step 6: Save the new summary into the database using relationships
        new_summary = self.summary_repo.create_summary(
            user=user,  # Pass the User object
            session=session,  # Pass the Session object
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