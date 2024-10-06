from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.summary_model import Summary
from models.user_model import User
from models.session_model import Session as UserSession
from typing import Optional, List
from utils.logger import logger


class SummaryRepository:
    def __init__(self, db: Session):
        self.db = db

    def fetch_summary(self, video_id: str, language_code: str) -> Optional[str]:
        """Fetch a summary based on video_id and language_code."""
        try:
            summary = self.db.query(Summary).filter(
                Summary.video_id == video_id,
                Summary.language_code == language_code
            ).first()
            if summary:
                logger.info(f"Fetched existing summary for video_id='{video_id}' and language_code='{language_code}'.")
                return summary.text_summary
        except SQLAlchemyError as e:
            logger.error(f"Error fetching summary: {str(e)}")
        return None

    def save_summary(self, user: User, session: UserSession, video_url: str, video_id: str, summary_version: str,
                     language_code: str, text_summary: str, video_duration: Optional[int] = None,
                     input_tokens: Optional[int] = None, output_tokens: Optional[int] = None,
                     summary_model: Optional[str] = None) -> Optional[Summary]:
        """Create and save a new summary."""
        try:
            new_summary = Summary(
                user=user,
                session=session,
                video_url=video_url,
                video_id=video_id,
                language_code=language_code,
                summary_version=summary_version,
                text_summary=text_summary,
                word_count=len(text_summary.split()),
                video_duration=video_duration,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                summary_model=summary_model
            )
            self.db.add(new_summary)
            self.db.commit()
            self.db.refresh(new_summary)
            logger.info(f"Saved new summary for video_id='{video_id}' and language_code='{language_code}'.")
            return new_summary
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error saving summary: {str(e)}")
            return None

    def get_user_summaries(self, user_id: int, limit: int = 10, offset: int = 0) -> List[Summary]:
        """Fetch a list of summaries for a given user."""
        try:
            summaries = self.db.query(Summary).filter(Summary.user_id == user_id)\
                .order_by(Summary.created_at.desc())\
                .limit(limit).offset(offset).all()
            return summaries
        except SQLAlchemyError as e:
            logger.error(f"Error fetching user summaries: {str(e)}")
            return []

    def delete_summary(self, summary_id: int) -> bool:
        """Delete a summary by its ID."""
        try:
            summary = self.db.query(Summary).filter(Summary.summary_id == summary_id).first()
            if summary:
                self.db.delete(summary)
                self.db.commit()
                logger.info(f"Deleted summary with ID {summary_id}")
                return True
            else:
                logger.warning(f"Summary with ID {summary_id} not found")
                return False
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting summary: {str(e)}")
            return False

    def update_summary(self, summary_id: int, **kwargs) -> Optional[Summary]:
        """Update an existing summary."""
        try:
            summary = self.db.query(Summary).filter(Summary.summary_id == summary_id).first()
            if summary:
                for key, value in kwargs.items():
                    setattr(summary, key, value)
                self.db.commit()
                self.db.refresh(summary)
                logger.info(f"Updated summary with ID {summary_id}")
                return summary
            else:
                logger.warning(f"Summary with ID {summary_id} not found")
                return None
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating summary: {str(e)}")
            return None