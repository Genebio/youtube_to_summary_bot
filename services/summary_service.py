from repositories.user_repository import UserRepository
from repositories.session_repository import SessionRepository
from repositories.summary_repository import SummaryRepository
from apis.fetch_transcript import fetch_youtube_transcript
from apis.summary import summarize_transcript
from apis.tts import convert_summary_to_speech
from config.config import OPENAI_CLIENT
from utils.formatter import extract_video_id, ServiceResponse
from utils.formatter import truncate_by_token_count


class SummaryService:
    def __init__(self, db):
        self.summary_repo = SummaryRepository(db)
        self.user_repo = UserRepository(db)
        self.session_repo = SessionRepository(db)

    def handle_error(self, session, error_message: str) -> ServiceResponse:
        """Helper to end session and return error response using the session object."""
        self.session_repo.end_session(session, end_reason=error_message)
        return ServiceResponse(error=error_message)

    async def fetch_transcript(self, video_url: str, user) -> ServiceResponse:
        """
        Fetches the transcript for the provided YouTube video.
        :param video_url: The URL of the YouTube video.
        :param user: The User object for the user requesting the transcript.
        :return: A ServiceResponse containing the transcript or an error message.
        """

        # Create a session for fetching the transcript (but do not end it here)
        session = self.session_repo.create_session(user_id=user.user_id)

        try:
            # Step 1: Extract video_id from video_url
            video_id_response = extract_video_id(video_url)
            if not video_id_response.is_success():
                return self.handle_error(session, video_id_response.error)
            video_id = video_id_response.data

            # Step 2: Fetch the transcript from YouTube
            transcript_response = await fetch_youtube_transcript(video_id)
            if not transcript_response.is_success():
                return self.handle_error(session, transcript_response.error)

            # Return the transcript data (with video_id and duration)
            transcript = truncate_by_token_count(transcript_response.data["transcript"])
            video_duration = transcript_response.data["video_duration"]
            return ServiceResponse(data={"transcript": transcript, "video_id": video_id, "video_duration": video_duration, "session": session})

        except Exception as e:
            return self.handle_error(session, str(e))

    async def summarize_transcript(self, transcript: str, video_url: str, video_id: str, video_duration: int, user, session, language_code: str = None) -> ServiceResponse:
        """
        Summarizes the provided transcript using the OpenAI API.
        :param transcript: The transcript text to summarize.
        :param video_url: The URL of the YouTube video.
        :param video_id: The video ID for which the summary is generated.
        :param video_duration: The duration of the video in seconds.
        :param user: The User object requesting the summary.
        :param session: The session object created earlier during transcript fetching.
        :param language_code: The language code for the summary (defaults to user's language code).
        :return: A ServiceResponse containing the summary or an error message.
        """

        try:
            # Use the user's language code if not provided
            final_language_code = language_code if language_code else user.language_code

            # Summarize the transcript using OpenAI API
            summary_response = await summarize_transcript(transcript, OPENAI_CLIENT, final_language_code)
            if not summary_response.is_success():
                return self.handle_error(session, summary_response.error)

            summary_text, input_tokens, output_tokens, summary_model = summary_response.data

            # Save the summary into the database
            new_summary = self.summary_repo.create_summary(
                user=user,
                session=session,
                video_url=video_url,
                video_id=video_id,
                language_code=final_language_code,
                text_summary=summary_text,
                video_duration=video_duration,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                summary_model=summary_model
            )

            # End the session after saving the summary
            self.session_repo.end_session(session, end_reason="Summary generated")
            return ServiceResponse(data=new_summary)

        except Exception as e:
            return self.handle_error(session, str(e))

    async def convert_summary_to_audio(self, summary_id: int, summary_text: str, user) -> ServiceResponse:
        """
        Converts the provided summary text to audio using the OpenAI TTS API.
        :param summary_id: The ID of the summary to convert to audio.
        :param summary_text: The text of the summary to convert to audio.
        :param user: The User object requesting the audio conversion.
        :return: A ServiceResponse containing the updated summary with TTS info or an error message.
        """

        # Create a session for audio conversion
        session = self.session_repo.create_session(user_id=user.user_id)

        try:
            # Convert the summary to audio using OpenAI TTS API
            tts_response = await convert_summary_to_speech(summary_text, OPENAI_CLIENT)
            if not tts_response.is_success():
                return self.handle_error(session, tts_response.error)

            tts_data = tts_response.data

            # Update the existing summary with TTS information
            updated_summary = self.summary_repo.update_summary_with_tts(
                summary_id=summary_id,
                requested_audio=True,
                got_audio=True,
                tts_model=tts_data['tts_model'],
                tts_tokens=tts_data['tts_tokens']
            )

            if not updated_summary:
                return self.handle_error(session, "Failed to update summary with TTS data")

            # End the session and return the updated summary
            self.session_repo.end_session(session, end_reason="Audio generated")
            return ServiceResponse(data=updated_summary)

        except Exception as e:
            return self.handle_error(session, str(e))