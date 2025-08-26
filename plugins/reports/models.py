# plugins/reports/models.py
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Report(Base):
    __tablename__ = "reports"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # e.g., order, user, sales
    created_at = Column(DateTime, default=datetime.utcnow)

class ReportData(Base):
    __tablename__ = "report_data"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    key = Column(String, nullable=False)
    value = Column(Float, nullable=False)

    report = relationship("Report", back_populates="data")

Report.data = relationship("ReportData", back_populates="report", cascade="all, delete-orphan")
