from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from utils.datetime_utils import get_formatted_time
from models.base import Base

class Summary(Base):
    __tablename__ = 'summaries'
    
    summary_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    session_id = Column(Integer, ForeignKey('sessions.session_id'), nullable=False)
    video_id = Column(String(50), nullable=False)
    video_url = Column(String(100), nullable=False)
    language_code = Column(String(10), nullable=False)
    text_summary = Column(Text)
    video_duration = Column(Integer, nullable=True)
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    summary_model = Column(String(100))
    created_at = Column(DateTime, default=get_formatted_time)

    # Unique constraint for video_id and language_code combination
    __table_args__ = (UniqueConstraint('video_id', 'language_code', name='_video_language_uc'),)

    # Relationships
    user = relationship("User", back_populates="summaries")
    session = relationship("Session", back_populates="summaries")
    
    def __init__(self, user, **kwargs):
        """
        Automatically capture the user's language_code at the time of summary creation.
        """
        if 'language_code' not in kwargs or kwargs['language_code'] is None:
            kwargs['language_code'] = user.language_code
        
        super().__init__(user=user, **kwargs)