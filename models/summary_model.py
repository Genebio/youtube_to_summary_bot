from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from config.config import ARMENIA_TZ
from .base import Base  # Import the Base model

class Summary(Base):
    __tablename__ = 'summaries'
    
    summary_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    session_id = Column(Integer, ForeignKey('sessions.session_id'))
    video_id = Column(String(50), nullable=False)
    language_code = Column(String(10), nullable=False)
    text_summary = Column(Text)
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    summary_model = Column(String(100))
    requested_audio = Column(Boolean, default=False)
    got_audio = Column(Boolean, default=False)
    tts_model = Column(String(100))
    tts_tokens = Column(Integer)
    created_at = Column(DateTime, default=datetime.now(ARMENIA_TZ))

    # Unique constraint for video_id and language_code combination
    __table_args__ = (UniqueConstraint('video_id', 'language_code', name='_video_language_uc'),)

    user = relationship("User", back_populates="summaries")
    session = relationship("Session", back_populates="summaries")