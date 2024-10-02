from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from utils.datetime_utils import get_formatted_time
from models.base import Base

class Summary(Base):
    __tablename__ = 'summaries'
    
    summary_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    session_id = Column(Integer, ForeignKey('sessions.session_id'))
    video_id = Column(String(50), nullable=False)
    video_url = Column(String(100), nullable=False)
    language_code = Column(String(10), nullable=True)
    text_summary = Column(Text)
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    summary_model = Column(String(100))
    requested_audio = Column(Boolean, default=False)
    got_audio = Column(Boolean, default=False)
    tts_model = Column(String(100))
    tts_tokens = Column(Integer)
    created_at = Column(DateTime, default=get_formatted_time())

    # Unique constraint for video_id and language_code combination
    __table_args__ = (UniqueConstraint('video_id', 'language_code', name='_video_language_uc'),)

    user = relationship("User", back_populates="summaries")
    session = relationship("Session", back_populates="summaries")

    def __init__(self, user, **kwargs):
        """
        Override init to inherit language_code from the user if not explicitly set.
        """
        if 'language_code' not in kwargs or kwargs['language_code'] is None:
            kwargs['language_code'] = user.language_code  # Inherit the language_code from the user
        
        super().__init__(user=user, **kwargs)