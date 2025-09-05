
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_type = Column(String, nullable=False)
    event_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="analytics_events")


# Minimal stubs to satisfy imports in CRUD/routes
class BusinessMetrics(Base):
    __tablename__ = "business_metrics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    total_revenue = Column(Integer, default=0)


class UserAnalytics(Base):
    __tablename__ = "user_analytics"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)


class SellerAnalytics(Base):
    __tablename__ = "seller_analytics"
    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, nullable=True)


class ProductAnalytics(Base):
    __tablename__ = "product_analytics"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=True)


class FinancialReport(Base):
    __tablename__ = "financial_reports"
    id = Column(Integer, primary_key=True, index=True)
    data = Column(JSON, nullable=True)


class PerformanceMetrics(Base):
    __tablename__ = "performance_metrics"
    id = Column(Integer, primary_key=True, index=True)
    data = Column(JSON, nullable=True)


class ReportTemplate(Base):
    __tablename__ = "report_templates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)


class ScheduledReport(Base):
    __tablename__ = "scheduled_reports"
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("report_templates.id"), nullable=True)


class ReportExecution(Base):
    __tablename__ = "report_executions"
    id = Column(Integer, primary_key=True, index=True)
    scheduled_report_id = Column(Integer, ForeignKey("scheduled_reports.id"), nullable=True)


class Dashboard(Base):
    __tablename__ = "dashboards"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)


class DataExport(Base):
    __tablename__ = "data_exports"
    id = Column(Integer, primary_key=True, index=True)
    format = Column(String, default="csv")
    data = Column(JSON, nullable=True)
