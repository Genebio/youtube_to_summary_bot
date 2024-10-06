from sqlalchemy.orm import Session
from models.session_model import Session as UserSession
from typing import Optional
from utils.datetime_utils import get_current_timestamp
from utils.memory_utils import get_current_ram_usage, get_ram_free_mb
from utils.logger import logger
import gc


class SessionRepository:
    """
    Repository for managing user sessions with memory tracking.
    Designed to work with FastAPI's dependency injection and existing db session management.
    """
    
    def __init__(self, db: Session):
        """
        Initialize repository with a database session from FastAPI's dependency injection.
        The db session lifecycle is managed by the get_db() dependency.
        
        Args:
            db: SQLAlchemy session provided by FastAPI dependency injection
        """
        self.db = db
        self._active_sessions = {}  # Track active sessions and their peak memory
    
    def create_session(self, user_id: int) -> UserSession:
        initial_ram_usage = get_current_ram_usage()
        
        new_session = UserSession(
            user_id=user_id,
            start_time=get_current_timestamp(),
            initial_ram_mb=initial_ram_usage,
            peak_ram_mb=initial_ram_usage,
            ram_free_mb=get_ram_free_mb()
        )
        
        self.db.add(new_session)
        self.db.flush()
        
        self._active_sessions[new_session.session_id] = {
            'peak_ram': initial_ram_usage,
            'start_ram': initial_ram_usage
        }
        
        logger.info(f"Created new session {new_session.session_id} for user {user_id} "
                    f"with initial RAM usage: {initial_ram_usage}MB")
        
        return new_session

    def update_peak_memory(self, session_id: int) -> None:
        """
        Update the peak memory usage for an active session.
        Should be called periodically during session lifetime.
        """
        if session_id in self._active_sessions:
            current_ram = get_current_ram_usage()
            if current_ram > self._active_sessions[session_id]['peak_ram']:
                self._active_sessions[session_id]['peak_ram'] = current_ram
                
                session = self.db.query(UserSession).get(session_id)
                if session:
                    session.peak_ram_mb = current_ram
                    self.db.flush()

    def end_session(self, session: UserSession, end_reason: str) -> Optional[UserSession]:
        try:
            final_ram_usage = get_current_ram_usage()
            session_data = self._active_sessions.get(session.session_id, {})
            peak_ram = session_data.get('peak_ram', final_ram_usage)
            start_ram = session_data.get('start_ram', session.initial_ram_mb)
            
            current_time = get_current_timestamp()
            
            session.shutdown_time = current_time
            session.session_duration_sec = current_time - session.start_time
            session.final_ram_mb = final_ram_usage
            session.peak_ram_mb = peak_ram
            session.ram_used_mb = final_ram_usage - start_ram
            session.ram_free_mb = get_ram_free_mb()
            session.session_end_reason = end_reason
            
            gc.collect()
            
            logger.info(
                f"Ended session {session.session_id} after {session.session_duration_sec}s. "
                f"Peak RAM: {peak_ram}MB, Final RAM: {final_ram_usage}MB, "
                f"Total RAM used: {session.ram_used_mb}MB"
            )
            
            return session
            
        except Exception as e:
            logger.error(f"Error ending session: {str(e)}")
            return None
        finally:
            if session.session_id in self._active_sessions:
                del self._active_sessions[session.session_id]