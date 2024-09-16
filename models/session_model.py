from sqlalchemy import Column, Integer, ForeignKey, DateTime, DECIMAL, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from config.config import ARMENIA_TZ
from .base import Base

class Session(Base):
    __tablename__ = 'sessions'
    
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    start_time = Column(DateTime, default=datetime.now(ARMENIA_TZ))
    shutdown_time = Column(DateTime)
    ram_usage_mb = Column(DECIMAL(10, 2))
    errors = Column(Text)
    session_duration_sec = Column(Integer)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    summaries = relationship("Summary", back_populates="session")
    costs = relationship("Cost", back_populates="session")