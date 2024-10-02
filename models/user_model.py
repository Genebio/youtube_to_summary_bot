from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from utils.datetime_utils import get_formatted_time
from models.base import Base

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    language_code = Column(String(10), default='en')
    current_subscription_status = Column(Boolean, default=False)
    created_at = Column(DateTime, default=get_formatted_time())
    
    # Relationships to other models
    sessions = relationship("Session", back_populates="user")
    summaries = relationship("Summary", back_populates="user")
