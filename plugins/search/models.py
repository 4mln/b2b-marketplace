from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class SavedSearch(Base):
    __tablename__ = "saved_searches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SearchEvent(Base):
    __tablename__ = "search_events"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


