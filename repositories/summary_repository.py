from sqlalchemy.orm import Session
from models.summary_model import Summary
from models.user_model import User
from models.session_model import Session as UserSession


class SummaryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_summary_by_video_and_language(self, video_id: str, language_code: str):
        """Fetch a summary based on video_id and language_code."""
        return self.db.query(Summary).filter(
            Summary.video_id == video_id,
            Summary.language_code == language_code
        ).first()

    def create_summary(self, user: User, session: UserSession, video_url: str, video_id: str, language_code: str,
                       text_summary: str, input_tokens: int, output_tokens: int, summary_model: str):
        """Create and save a new summary using relationships for User and Session."""
        new_summary = Summary(
            user=user,  # Pass the User object here
            session=session,  # Pass the Session object here
            video_url=video_url,
            video_id=video_id,
            language_code=language_code,
            text_summary=text_summary,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            summary_model=summary_model,
            requested_audio=False,
            got_audio=False,
        )
        self.db.add(new_summary)
        self.db.commit()
        self.db.refresh(new_summary)  # This will populate the auto-incremented summary_id
        return new_summary

    def update_summary_with_tts(self, summary_id: int, requested_audio: bool, got_audio: bool,
                                tts_model: str = None, tts_tokens: int = 0):
        """Update an existing summary with TTS-related information."""
        summary = self.db.query(Summary).filter(Summary.summary_id == summary_id).first()

        if not summary:
            return None

        summary.requested_audio = requested_audio
        summary.got_audio = got_audio
        summary.tts_model = tts_model
        summary.tts_tokens = tts_tokens

        self.db.commit()
        self.db.refresh(summary)
        return summary