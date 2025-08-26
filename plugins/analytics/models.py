# plugins/analytics/models.py
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db.base import Base

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    event_type = Column(String, nullable=False)
    metadata = Column(String, nullable=True)  # JSON as string
    created_at = Column(DateTime, default=datetime.utcnow)
