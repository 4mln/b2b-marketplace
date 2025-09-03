"""
Analytics & Reporting System Routes
FastAPI endpoints for comprehensive business intelligence and reporting
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import json

from app.core.auth import get_current_user_sync as get_current_user
from plugins.auth.models import User
from . import crud
from .schemas import (
    AnalyticsEventCreate, AnalyticsEventOut, BusinessMetricsOut, UserAnalyticsOut,
    SellerAnalyticsOut, ProductAnalyticsOut, FinancialReportOut, PerformanceMetricsOut,
    ReportTemplateCreate, ReportTemplateUpdate, ReportTemplateOut,
    ScheduledReportCreate, ScheduledReportUpdate, ScheduledReportOut,
    ReportExecutionOut, DashboardCreate, DashboardUpdate, DashboardOut,
    DataExportCreate, DataExportOut, AnalyticsQueryRequest, AnalyticsQueryResponse,
    BusinessMetricsSummary, PerformanceSummary, ReportGenerationRequest,
    ReportGenerationResponse, RealTimeMetrics, AnalyticsRequest, AnalyticsResponse
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


# Lazy generator-style DB dependency to avoid circular imports
def db_dep():
    from app.db.session import get_db_sync
    yield from get_db_sync()


# Analytics Events
@router.post("/events", response_model=AnalyticsEventOut)
def create_analytics_event(
    event_data: AnalyticsEventCreate,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Create an analytics event"""
    return crud.create_analytics_event(db, event_data)


@router.get("/events/{event_id}", response_model=AnalyticsEventOut)
def get_analytics_event(
    event_id: int,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get analytics event by ID"""
    event = crud.get_analytics_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Analytics event not found")
    return event


@router.get("/events", response_model=List[AnalyticsEventOut])
def get_analytics_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    event_types: Optional[str] = Query(None, description="Comma-separated event types"),
    user_id: Optional[int] = Query(None),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get analytics events with filtering"""
    # Parse event types
    parsed_event_types = None
    if event_types:
        parsed_event_types = [event_types.strip() for event_types in event_types.split(",")]
    
    events, total = crud.get_analytics_events(
        db, skip, limit, parsed_event_types, user_id,
        entity_type, entity_id, start_date, end_date
    )
    return events


@router.post("/query", response_model=AnalyticsQueryResponse)
def query_analytics(
    query_request: AnalyticsQueryRequest,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Advanced analytics query"""
    return crud.query_analytics_events(db, query_request)


# Business Metrics
@router.get("/business-metrics", response_model=List[BusinessMetricsOut])
def get_business_metrics(
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get business metrics for date range"""
    metrics, total = crud.get_business_metrics(db, start_date, end_date, skip, limit)
    return metrics


@router.get("/business-metrics/summary", response_model=BusinessMetricsSummary)
def get_business_metrics_summary(
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get business metrics summary"""
    return crud.calculate_business_metrics_summary(db, start_date, end_date)


# User Analytics
@router.get("/users/{user_id}/analytics", response_model=List[UserAnalyticsOut])
def get_user_analytics(
    user_id: int,
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get user analytics for date range"""
    analytics, total = crud.get_user_analytics(db, user_id, start_date, end_date, skip, limit)
    return analytics


@router.get("/me/analytics", response_model=List[UserAnalyticsOut])
def get_my_analytics(
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get current user's analytics"""
    analytics, total = crud.get_user_analytics(db, current_user.id, start_date, end_date, skip, limit)
    return analytics


# Seller Analytics
@router.get("/sellers/{seller_id}/analytics", response_model=List[SellerAnalyticsOut])
def get_seller_analytics(
    seller_id: int,
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get seller analytics for date range"""
    analytics, total = crud.get_seller_analytics(db, seller_id, start_date, end_date, skip, limit)
    return analytics


# Product Analytics
@router.get("/products/{product_id}/analytics", response_model=List[ProductAnalyticsOut])
def get_product_analytics(
    product_id: int,
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get product analytics for date range"""
    analytics, total = crud.get_product_analytics(db, product_id, start_date, end_date, skip, limit)
    return analytics


# Financial Reports
@router.get("/financial-reports", response_model=List[FinancialReportOut])
def get_financial_reports(
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    report_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get financial reports for date range"""
    reports, total = crud.get_financial_reports(db, start_date, end_date, report_type, skip, limit)
    return reports


# Performance Metrics
@router.get("/performance-metrics", response_model=List[PerformanceMetricsOut])
def get_performance_metrics(
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    metric_type: Optional[str] = Query(None),
    metric_name: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get performance metrics for date range"""
    metrics, total = crud.get_performance_metrics(db, start_date, end_date, metric_type, metric_name, skip, limit)
    return metrics


@router.get("/performance/summary", response_model=PerformanceSummary)
def get_performance_summary(
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get performance summary"""
    return crud.calculate_performance_summary(db, start_date, end_date)


# Report Templates
@router.post("/templates", response_model=ReportTemplateOut)
def create_report_template(
    template_data: ReportTemplateCreate,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Create report template"""
    return crud.create_report_template(db, template_data)


@router.get("/templates/{template_id}", response_model=ReportTemplateOut)
def get_report_template(
    template_id: int,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get report template by ID"""
    template = crud.get_report_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Report template not found")
    return template


@router.get("/templates", response_model=List[ReportTemplateOut])
def get_report_templates(
    report_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get report templates with filtering"""
    templates, total = crud.get_report_templates(db, report_type, is_active, skip, limit)
    return templates


@router.put("/templates/{template_id}", response_model=ReportTemplateOut)
def update_report_template(
    template_id: int,
    template_data: ReportTemplateUpdate,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Update report template"""
    template = crud.update_report_template(db, template_id, template_data)
    if not template:
        raise HTTPException(status_code=404, detail="Report template not found")
    return template


@router.delete("/templates/{template_id}")
def delete_report_template(
    template_id: int,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Delete report template"""
    success = crud.delete_report_template(db, template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Report template not found")
    return {"message": "Report template deleted successfully"}


# Scheduled Reports
@router.post("/scheduled-reports", response_model=ScheduledReportOut)
def create_scheduled_report(
    report_data: ScheduledReportCreate,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Create scheduled report"""
    return crud.create_scheduled_report(db, report_data)


@router.get("/scheduled-reports", response_model=List[ScheduledReportOut])
def get_scheduled_reports(
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get scheduled reports"""
    reports, total = crud.get_scheduled_reports(db, is_active, skip, limit)
    return reports


@router.put("/scheduled-reports/{report_id}", response_model=ScheduledReportOut)
def update_scheduled_report(
    report_id: int,
    report_data: ScheduledReportUpdate,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Update scheduled report"""
    report = crud.update_scheduled_report(db, report_id, report_data)
    if not report:
        raise HTTPException(status_code=404, detail="Scheduled report not found")
    return report


@router.delete("/scheduled-reports/{report_id}")
def delete_scheduled_report(
    report_id: int,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Delete scheduled report"""
    success = crud.delete_scheduled_report(db, report_id)
    if not success:
        raise HTTPException(status_code=404, detail="Scheduled report not found")
    return {"message": "Scheduled report deleted successfully"}


# Report Execution
@router.get("/executions/{execution_id}", response_model=ReportExecutionOut)
def get_report_execution(
    execution_id: int,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get report execution by ID"""
    execution = crud.get_report_execution(db, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Report execution not found")
    return execution


@router.post("/generate-report", response_model=ReportGenerationResponse)
def generate_report(
    request: ReportGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Generate a report"""
    return crud.generate_report(db, request)


# Dashboards
@router.post("/dashboards", response_model=DashboardOut)
def create_dashboard(
    dashboard_data: DashboardCreate,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Create dashboard"""
    return crud.create_dashboard(db, dashboard_data)


@router.get("/dashboards/{dashboard_id}", response_model=DashboardOut)
def get_dashboard(
    dashboard_id: int,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard by ID"""
    dashboard = crud.get_dashboard(db, dashboard_id)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dashboard


@router.get("/dashboards", response_model=List[DashboardOut])
def get_user_dashboards(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get current user's dashboards"""
    dashboards, total = crud.get_user_dashboards(db, current_user.id, skip, limit)
    return dashboards


@router.put("/dashboards/{dashboard_id}", response_model=DashboardOut)
def update_dashboard(
    dashboard_id: int,
    dashboard_data: DashboardUpdate,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Update dashboard"""
    dashboard = crud.update_dashboard(db, dashboard_id, dashboard_data)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dashboard


@router.delete("/dashboards/{dashboard_id}")
def delete_dashboard(
    dashboard_id: int,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Delete dashboard"""
    success = crud.delete_dashboard(db, dashboard_id)
    if not success:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return {"message": "Dashboard deleted successfully"}


# Data Exports
@router.post("/exports", response_model=DataExportOut)
def create_data_export(
    export_data: DataExportCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Create data export request"""
    return crud.create_data_export(db, export_data)


@router.get("/exports/{export_id}", response_model=DataExportOut)
def get_data_export(
    export_id: int,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get data export by ID"""
    export = crud.get_data_export(db, export_id)
    if not export:
        raise HTTPException(status_code=404, detail="Data export not found")
    return export


@router.get("/exports", response_model=List[DataExportOut])
def get_user_exports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get current user's data exports"""
    exports, total = crud.get_user_exports(db, current_user.id, skip, limit)
    return exports


# Real-time Analytics
@router.get("/real-time", response_model=RealTimeMetrics)
def get_real_time_metrics(
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get real-time metrics"""
    return crud.get_real_time_metrics(db)


# Utility Endpoints
@router.post("/track-event", response_model=AnalyticsEventOut)
def track_event(
    event_type: str,
    event_name: str,
    user_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    event_data: Optional[dict] = None,
    session_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Track an analytics event"""
    from .models import AnalyticsEventType
    
    try:
        event_type_enum = AnalyticsEventType(event_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid event type")
    
    return crud.track_event(
        db, event_type_enum, event_name, user_id, entity_type,
        entity_id, event_data, session_id, ip_address, user_agent
    )


@router.post("/calculate-daily-metrics")
def calculate_daily_metrics(
    date: datetime = Query(..., description="Date to calculate metrics for"),
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Calculate daily business metrics"""
    metrics = crud.calculate_daily_metrics(db, date)
    return {"message": "Daily metrics calculated successfully", "metrics": metrics}


@router.post("/cleanup")
def cleanup_old_analytics(
    days: int = Query(90, ge=1, le=365, description="Days to keep"),
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Clean up old analytics data"""
    deleted_count = crud.cleanup_old_analytics(db, days)
    return {"message": f"Cleaned up {deleted_count} old records"}


# Analytics Dashboard Endpoints
@router.get("/dashboard/overview")
def get_analytics_overview(
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get analytics dashboard overview"""
    business_summary = crud.calculate_business_metrics_summary(db, start_date, end_date)
    performance_summary = crud.calculate_performance_summary(db, start_date, end_date)
    real_time_metrics = crud.get_real_time_metrics(db)
    
    return {
        "business_metrics": business_summary,
        "performance_metrics": performance_summary,
        "real_time_metrics": real_time_metrics,
        "date_range": {"start": start_date, "end": end_date}
    }


@router.get("/dashboard/user-activity")
def get_user_activity_analytics(
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get user activity analytics"""
    # Get user registration events
    registrations, _ = crud.get_analytics_events(
        db, 0, 1000, ["user_registration"], None, None, None, start_date, end_date
    )
    
    # Get user login events
    logins, _ = crud.get_analytics_events(
        db, 0, 1000, ["user_login"], None, None, None, start_date, end_date
    )
    
    # Get user search events
    searches, _ = crud.get_analytics_events(
        db, 0, 1000, ["search"], None, None, None, start_date, end_date
    )
    
    return {
        "registrations": len(registrations),
        "logins": len(logins),
        "searches": len(searches),
        "date_range": {"start": start_date, "end": end_date}
    }


@router.get("/dashboard/seller-performance")
def get_seller_performance_analytics(
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get seller performance analytics"""
    # Get product creation events
    product_creations, _ = crud.get_analytics_events(
        db, 0, 1000, ["product_create"], None, "product", None, start_date, end_date
    )
    
    # Get order events
    orders, _ = crud.get_analytics_events(
        db, 0, 1000, ["order_create"], None, "order", None, start_date, end_date
    )
    
    return {
        "products_created": len(product_creations),
        "orders_placed": len(orders),
        "date_range": {"start": start_date, "end": end_date}
    }