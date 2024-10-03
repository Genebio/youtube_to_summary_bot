from sqlalchemy.orm import Session
from models.session_model import Session as UserSession
from typing import Optional
from utils.datetime_utils import get_formatted_time


class SessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, user_id: int, ram_usage_mb: float) -> UserSession:
        """
        Create and save a new session for the given user with initial RAM usage.
        """
        new_session = UserSession(
            user_id=user_id,
            start_time=get_formatted_time(),  # Set the start time when session is created
            ram_usage_mb=ram_usage_mb  # Initial RAM usage
        )
        self.db.add(new_session)
        self.db.commit()
        self.db.refresh(new_session)  # Populate the session_id
        return new_session

    def get_session_by_id(self, session_id: int) -> Optional[UserSession]:
        """
        Fetch a session based on its session_id.
        Returns None if the session is not found.
        """
        return self.db.query(UserSession).filter(UserSession.session_id == session_id).first()

    def end_session(self, session_id: int, ram_usage_mb: float, end_reason: str) -> Optional[UserSession]:
        """
        End a session by updating the shutdown time, session duration, and reason for session termination.
        """
        session = self.get_session_by_id(session_id)
        if not session:
            return None

        session.shutdown_time = get_formatted_time()  # Set the end time
        session.ram_usage_mb = ram_usage_mb  # Update the RAM usage
        session.session_end_reason = end_reason  # Set the reason why the session ended
        session.session_duration_sec = (session.shutdown_time - session.start_time).total_seconds()

        self.db.commit()
        self.db.refresh(session)
        return session