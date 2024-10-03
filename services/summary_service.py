from repositories.user_repository import UserRepository
from repositories.session_repository import SessionRepository
from repositories.summary_repository import SummaryRepository
from apis.fetch_transcript import fetch_youtube_transcript
from apis.summary import summarize_transcript
from apis.tts import convert_summary_to_speech
from config.config import OPENAI_CLIENT
from utils.formatter import extract_video_id, ServiceResponse


class SummaryService:
    def __init__(self, db):
        self.summary_repo = SummaryRepository(db)
        self.user_repo = UserRepository(db)
        self.session_repo = SessionRepository(db)

    def handle_error(self, session_id: int, error_message: str) -> ServiceResponse:
        """Helper to end session and return error response."""
        self.session_repo.end_session(session_id, end_reason=error_message)
        return ServiceResponse(error=error_message)

    async def process_summary(self, video_url: str, user_id: int, language_code: str = None) -> ServiceResponse:
        """
        Handles the main logic for fetching the transcript and summarizing it.
        :param video_url: The URL of the YouTube video.
        :param user_id: The ID of the user requesting the summary.
        :param language_code: The language code for the summary. If None or empty, defaults to the user's language code.
        :return: A ServiceResponse containing either the summary or an error message.
        """

        session = self.session_repo.create_session(user_id=user_id)
        try:
            # Step 1: Extract video_id from video_url
            video_id_response = extract_video_id(video_url)
            if not video_id_response.is_success():
                return self.handle_error(session.session_id, video_id_response.error)
            video_id = video_id_response.data

            # Step 2: Fetch the user
            user = self.user_repo.get_user_by_id(user_id)
            if not user:
                return self.handle_error(session.session_id, "User not found")

            # Step 3: Fetch the language code - use the provided one if not empty, else default to user's language code
            final_language_code = language_code if language_code else user.language_code
            if not final_language_code:
                return self.handle_error(session.session_id, "Language code not set for user")

            # Step 4: Fetch the transcript from YouTube
            transcript_response = await fetch_youtube_transcript(video_id)
            if not transcript_response.is_success():
                return self.handle_error(session.session_id, transcript_response.error)
            transcript = transcript_response.data

            # Step 5: Summarize the transcript using OpenAI API
            summary_response = await summarize_transcript(transcript, OPENAI_CLIENT, final_language_code)
            if not summary_response.is_success():
                return self.handle_error(session.session_id, summary_response.error)
            summary_text, input_tokens, output_tokens, summary_model = summary_response.data

            # Step 6: Save the new summary into the database using relationships
            new_summary = self.summary_repo.create_summary(
                user=user,
                session=session,
                video_url=video_url,
                video_id=video_id,
                language_code=final_language_code,
                text_summary=summary_text,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                summary_model=summary_model
            )

            # Step 7: End the session
            self.session_repo.end_session(session.session_id, end_reason="Summary generated")
            return ServiceResponse(data=new_summary)

        except Exception as e:
            # Handle any unexpected errors
            return self.handle_error(session.session_id, str(e))

    async def process_summary_to_audio(self, user_id: int, summary_id: int, summary_text: str) -> ServiceResponse:
        """Handles the optional TTS conversion of a summary to audio."""
        session = self.session_repo.create_session(user_id=user_id)

        try:
            # Step 1: Convert the summary to audio using OpenAI TTS API
            tts_response = await convert_summary_to_speech(summary_text, OPENAI_CLIENT)
            if not tts_response.is_success():
                return self.handle_error(session.session_id, tts_response.error)

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
                return self.handle_error(session.session_id, "Failed to update summary with TTS data")

            # End the session and return the updated summary
            self.session_repo.end_session(session.session_id, end_reason="Audio generated")
            return ServiceResponse(data=updated_summary)

        except Exception as e:
            # Handle any unexpected errors
            return self.handle_error(session.session_id, str(e))