from sqlalchemy.orm import Session
from models.session_model import Session as UserSession
from typing import Optional
from utils.datetime_utils import get_formatted_time
from utils.memory_utils import get_current_ram_usage, get_ram_free_mb


class SessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, user_id: int) -> UserSession:
        """
        Create and save a new session for the given user with initial RAM usage.
        Start tracking RAM usage.
        """
        initial_ram_usage = get_current_ram_usage()

        new_session = UserSession(
            user_id=user_id,
            start_time=get_formatted_time(),  # Set the start time when session is created
            ram_usage_mb=initial_ram_usage  # Store initial RAM usage as an integer
        )
        self.db.add(new_session)
        self.db.commit()
        self.db.refresh(new_session)  # Populate the session_id
        return new_session

    def end_session(self, session_id: int, end_reason: str) -> Optional[UserSession]:
        """
        End a session by updating the shutdown time, session duration, and reason for session termination.
        Track RAM used during the session and free RAM left.
        """
        session = self.get_session_by_id(session_id)
        if not session:
            return None

        # Capture the final RAM usage at the end of the session
        final_ram_usage = get_current_ram_usage()

        # Calculate the RAM used during the session (absolute value of the difference)
        ram_used = abs(session.ram_usage_mb - final_ram_usage)

        session.shutdown_time = get_formatted_time()  # Set the end time
        session.ram_usage_mb = ram_used  # Update the session with the RAM used (as a whole number)
        session.ram_free_mb = get_ram_free_mb()  # Store the free RAM left
        session.session_end_reason = end_reason  # Set the reason why the session ended
        session.session_duration_sec = (session.shutdown_time - session.start_time).total_seconds()

        self.db.commit()
        self.db.refresh(session)
        return session