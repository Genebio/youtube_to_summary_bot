from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from models.base import Base

class Session(Base):
    __tablename__ = 'sessions'
    
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    start_time = Column(Integer)
    shutdown_time = Column(Integer)
    initial_ram_mb = Column(Integer)
    peak_ram_mb = Column(Integer)
    final_ram_mb = Column(Integer)
    ram_used_mb = Column(Integer)
    ram_free_mb = Column(Integer)
    session_end_reason = Column(Text)
    session_duration_sec = Column(Integer)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    summaries = relationship("Summary", back_populates="session")