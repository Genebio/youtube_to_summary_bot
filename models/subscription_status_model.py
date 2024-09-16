from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from config.config import ARMENIA_TZ
from .base import Base

class SubscriptionStatus(Base):
    __tablename__ = 'subscription_status'
    
    subscription_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    status = Column(Boolean)
    start_time = Column(DateTime, default=datetime.now(ARMENIA_TZ))
    end_time = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="subscription_status_history")