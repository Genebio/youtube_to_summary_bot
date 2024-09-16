from sqlalchemy import Column, Integer, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Cost(Base):
    __tablename__ = 'costs'
    
    cost_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    session_id = Column(Integer, ForeignKey('sessions.session_id'))
    summary_id = Column(Integer, ForeignKey('summaries.summary_id'))
    gpt_cost = Column(DECIMAL(10, 2))
    tts_cost = Column(DECIMAL(10, 2))
    total_cost = Column(DECIMAL(10, 2))
    
    # Relationships
    user = relationship("User", back_populates="costs")
    session = relationship("Session", back_populates="costs")
    summary = relationship("Summary", back_populates="costs")