from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from models.base import Base

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    language_code = Column(String(10), default='en')
    subscription = Column(Boolean, default=False)
    created_at = Column(Integer)
    
    # Relationships to other models
    sessions = relationship("Session", back_populates="user")
    summaries = relationship("Summary", back_populates="user")
