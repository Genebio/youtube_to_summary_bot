from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from utils.datetime_utils import get_formatted_time
from .base import Base

class SubscriptionStatus(Base):
    __tablename__ = 'subscription_status'
    
    subscription_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    status = Column(Boolean)
    start_time = Column(DateTime, default=get_formatted_time())
    end_time = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="subscription_status_history")