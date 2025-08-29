from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class BannedItem(Base):
    __tablename__ = "banned_items"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor = Column(String, nullable=False)
    action = Column(String, nullable=False)
    entity = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


