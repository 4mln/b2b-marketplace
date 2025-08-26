# plugins/test_connections/models.py
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db.base import Base

class ConnectionTest(Base):
    __tablename__ = "connection_tests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    checked_at = Column(DateTime, default=datetime.utcnow)
