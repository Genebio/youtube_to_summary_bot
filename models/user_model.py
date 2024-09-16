from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    language_code = Column(String(10))
    current_subscription_status = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(datetime.UTC))
    
    # Relationships to other models
    sessions = relationship("Session", back_populates="user")
    summaries = relationship("Summary", back_populates="user")
    subscription_status_history = relationship("SubscriptionStatus", back_populates="user")
    costs = relationship("Cost", back_populates="user")