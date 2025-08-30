"""
Analytics & Reporting System CRUD Operations
Comprehensive business intelligence and reporting for the B2B marketplace
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc, text, case, extract
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import json
import csv
import io
from decimal import Decimal

from .models import (
    AnalyticsEvent, BusinessMetrics, UserAnalytics, SellerAnalytics, ProductAnalytics,
    FinancialReport, PerformanceMetrics, ReportTemplate, ScheduledReport, ReportExecution,
    Dashboard, DataExport, AnalyticsEventType
)
from .schemas import (
    AnalyticsEventCreate, AnalyticsEventOut, BusinessMetricsCreate, BusinessMetricsOut,
    UserAnalyticsCreate, UserAnalyticsOut, SellerAnalyticsCreate, SellerAnalyticsOut,
    ProductAnalyticsCreate, ProductAnalyticsOut, FinancialReportCreate, FinancialReportOut,
    PerformanceMetricsCreate, PerformanceMetricsOut, ReportTemplateCreate, ReportTemplateUpdate, ReportTemplateOut,
    ScheduledReportCreate, ScheduledReportUpdate, ScheduledReportOut, ReportExecutionCreate, ReportExecutionOut,
    DashboardCreate, DashboardUpdate, DashboardOut, DataExportCreate, DataExportOut,
    AnalyticsQueryRequest, AnalyticsQueryResponse, BusinessMetricsSummary, PerformanceSummary,
    ReportGenerationRequest, ReportGenerationResponse, RealTimeMetrics, AnalyticsRequest, AnalyticsResponse
)


# Analytics Event CRUD Operations
def create_analytics_event(db: Session, event_data: AnalyticsEventCreate) -> AnalyticsEventOut:
    """Create a new analytics event"""
    db_event = AnalyticsEvent(**event_data.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return AnalyticsEventOut.from_orm(db_event)


def get_analytics_event(db: Session, event_id: int) -> Optional[AnalyticsEventOut]:
    """Get analytics event by ID"""
    db_event = db.query(AnalyticsEvent).filter(AnalyticsEvent.id == event_id).first()
    return AnalyticsEventOut.from_orm(db_event) if db_event else None


def get_analytics_events(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    event_types: Optional[List[AnalyticsEventType]] = None,
    user_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Tuple[List[AnalyticsEventOut], int]:
    """Get analytics events with filtering"""
    query = db.query(AnalyticsEvent)
    
    if event_types:
        query = query.filter(AnalyticsEvent.event_type.in_([et.value for et in event_types]))
    if user_id:
        query = query.filter(AnalyticsEvent.user_id == user_id)
    if entity_type:
        query = query.filter(AnalyticsEvent.entity_type == entity_type)
    if entity_id:
        query = query.filter(AnalyticsEvent.entity_id == entity_id)
    if start_date:
        query = query.filter(AnalyticsEvent.created_at >= start_date)
    if end_date:
        query = query.filter(AnalyticsEvent.created_at <= end_date)
    
    total = query.count()
    events = query.order_by(desc(AnalyticsEvent.created_at)).offset(skip).limit(limit).all()
    
    return [AnalyticsEventOut.from_orm(event) for event in events], total


def query_analytics_events(db: Session, query_request: AnalyticsQueryRequest) -> AnalyticsQueryResponse:
    """Advanced analytics query"""
    start_time = datetime.utcnow()
    
    query = db.query(AnalyticsEvent)
    
    # Apply filters
    if query_request.event_types:
        query = query.filter(AnalyticsEvent.event_type.in_([et.value for et in query_request.event_types]))
    if query_request.entity_types:
        query = query.filter(AnalyticsEvent.entity_type.in_(query_request.entity_types))
    if query_request.user_ids:
        query = query.filter(AnalyticsEvent.user_id.in_(query_request.user_ids))
    if query_request.start_date:
        query = query.filter(AnalyticsEvent.created_at >= query_request.start_date)
    if query_request.end_date:
        query = query.filter(AnalyticsEvent.created_at <= query_request.end_date)
    
    # Apply custom filters
    if query_request.filters:
        for field, value in query_request.filters.items():
            if hasattr(AnalyticsEvent, field):
                query = query.filter(getattr(AnalyticsEvent, field) == value)
    
    # Group by
    if query_request.group_by:
        group_columns = []
        for group_field in query_request.group_by:
            if hasattr(AnalyticsEvent, group_field):
                group_columns.append(getattr(AnalyticsEvent, group_field))
        
        if group_columns:
            query = query.group_by(*group_columns)
    
    # Apply limit
    query = query.limit(query_request.limit)
    
    # Execute query
    results = query.all()
    
    # Convert to dict format
    result_data = []
    for result in results:
        result_dict = {
            'id': result.id,
            'event_type': result.event_type,
            'event_name': result.event_name,
            'created_at': result.created_at.isoformat(),
            'user_id': result.user_id,
            'entity_type': result.entity_type,
            'entity_id': result.entity_id
        }
        if result.event_data:
            result_dict.update(result.event_data)
        result_data.append(result_dict)
    
    query_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
    
    return AnalyticsQueryResponse(
        results=result_data,
        total=len(result_data),
        query_time_ms=query_time_ms
    )


# Business Metrics CRUD Operations
def create_business_metrics(db: Session, metrics_data: BusinessMetricsCreate) -> BusinessMetricsOut:
    """Create business metrics"""
    db_metrics = BusinessMetrics(**metrics_data.dict())
    db.add(db_metrics)
    db.commit()
    db.refresh(db_metrics)
    return BusinessMetricsOut.from_orm(db_metrics)


def get_business_metrics(
    db: Session,
    start_date: datetime,
    end_date: datetime,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[BusinessMetricsOut], int]:
    """Get business metrics for date range"""
    query = db.query(BusinessMetrics).filter(
        BusinessMetrics.date >= start_date,
        BusinessMetrics.date <= end_date
    )
    
    total = query.count()
    metrics = query.order_by(desc(BusinessMetrics.date)).offset(skip).limit(limit).all()
    
    return [BusinessMetricsOut.from_orm(metric) for metric in metrics], total


def calculate_business_metrics_summary(db: Session, start_date: datetime, end_date: datetime) -> BusinessMetricsSummary:
    """Calculate business metrics summary"""
    # Get latest metrics for summary
    latest_metrics = db.query(BusinessMetrics).filter(
        BusinessMetrics.date >= start_date,
        BusinessMetrics.date <= end_date
    ).order_by(desc(BusinessMetrics.date)).first()
    
    if not latest_metrics:
        return BusinessMetricsSummary(
            total_users=0,
            total_sellers=0,
            total_products=0,
            total_orders=0,
            total_revenue=Decimal('0'),
            avg_order_value=Decimal('0'),
            user_growth_rate=0.0,
            revenue_growth_rate=0.0,
            date_range={"start": start_date, "end": end_date}
        )
    
    # Calculate growth rates
    previous_start = start_date - (end_date - start_date)
    previous_metrics = db.query(BusinessMetrics).filter(
        BusinessMetrics.date >= previous_start,
        BusinessMetrics.date < start_date
    ).order_by(desc(BusinessMetrics.date)).first()
    
    user_growth_rate = 0.0
    revenue_growth_rate = 0.0
    
    if previous_metrics:
        if previous_metrics.total_users > 0:
            user_growth_rate = ((latest_metrics.total_users - previous_metrics.total_users) / previous_metrics.total_users) * 100
        if previous_metrics.total_revenue > 0:
            revenue_growth_rate = ((latest_metrics.total_revenue - previous_metrics.total_revenue) / previous_metrics.total_revenue) * 100
    
    return BusinessMetricsSummary(
        total_users=latest_metrics.total_users,
        total_sellers=latest_metrics.total_sellers,
        total_products=latest_metrics.total_products,
        total_orders=latest_metrics.total_orders,
        total_revenue=latest_metrics.total_revenue,
        avg_order_value=latest_metrics.avg_order_value,
        user_growth_rate=user_growth_rate,
        revenue_growth_rate=revenue_growth_rate,
        date_range={"start": start_date, "end": end_date}
    )


# User Analytics CRUD Operations
def create_user_analytics(db: Session, analytics_data: UserAnalyticsCreate) -> UserAnalyticsOut:
    """Create user analytics"""
    db_analytics = UserAnalytics(**analytics_data.dict())
    db.add(db_analytics)
    db.commit()
    db.refresh(db_analytics)
    return UserAnalyticsOut.from_orm(db_analytics)


def get_user_analytics(
    db: Session,
    user_id: int,
    start_date: datetime,
    end_date: datetime,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[UserAnalyticsOut], int]:
    """Get user analytics for date range"""
    query = db.query(UserAnalytics).filter(
        UserAnalytics.user_id == user_id,
        UserAnalytics.date >= start_date,
        UserAnalytics.date <= end_date
    )
    
    total = query.count()
    analytics = query.order_by(desc(UserAnalytics.date)).offset(skip).limit(limit).all()
    
    return [UserAnalyticsOut.from_orm(analytics) for analytics in analytics], total


# Seller Analytics CRUD Operations
def create_seller_analytics(db: Session, analytics_data: SellerAnalyticsCreate) -> SellerAnalyticsOut:
    """Create seller analytics"""
    db_analytics = SellerAnalytics(**analytics_data.dict())
    db.add(db_analytics)
    db.commit()
    db.refresh(db_analytics)
    return SellerAnalyticsOut.from_orm(db_analytics)


def get_seller_analytics(
    db: Session,
    seller_id: int,
    start_date: datetime,
    end_date: datetime,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[SellerAnalyticsOut], int]:
    """Get seller analytics for date range"""
    query = db.query(SellerAnalytics).filter(
        SellerAnalytics.seller_id == seller_id,
        SellerAnalytics.date >= start_date,
        SellerAnalytics.date <= end_date
    )
    
    total = query.count()
    analytics = query.order_by(desc(SellerAnalytics.date)).offset(skip).limit(limit).all()
    
    return [SellerAnalyticsOut.from_orm(analytics) for analytics in analytics], total


# Product Analytics CRUD Operations
def create_product_analytics(db: Session, analytics_data: ProductAnalyticsCreate) -> ProductAnalyticsOut:
    """Create product analytics"""
    db_analytics = ProductAnalytics(**analytics_data.dict())
    db.add(db_analytics)
    db.commit()
    db.refresh(db_analytics)
    return ProductAnalyticsOut.from_orm(db_analytics)


def get_product_analytics(
    db: Session,
    product_id: int,
    start_date: datetime,
    end_date: datetime,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[ProductAnalyticsOut], int]:
    """Get product analytics for date range"""
    query = db.query(ProductAnalytics).filter(
        ProductAnalytics.product_id == product_id,
        ProductAnalytics.date >= start_date,
        ProductAnalytics.date <= end_date
    )
    
    total = query.count()
    analytics = query.order_by(desc(ProductAnalytics.date)).offset(skip).limit(limit).all()
    
    return [ProductAnalyticsOut.from_orm(analytics) for analytics in analytics], total


# Financial Report CRUD Operations
def create_financial_report(db: Session, report_data: FinancialReportCreate) -> FinancialReportOut:
    """Create financial report"""
    db_report = FinancialReport(**report_data.dict())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return FinancialReportOut.from_orm(db_report)


def get_financial_reports(
    db: Session,
    start_date: datetime,
    end_date: datetime,
    report_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[FinancialReportOut], int]:
    """Get financial reports for date range"""
    query = db.query(FinancialReport).filter(
        FinancialReport.report_date >= start_date,
        FinancialReport.report_date <= end_date
    )
    
    if report_type:
        query = query.filter(FinancialReport.report_type == report_type)
    
    total = query.count()
    reports = query.order_by(desc(FinancialReport.report_date)).offset(skip).limit(limit).all()
    
    return [FinancialReportOut.from_orm(report) for report in reports], total


# Performance Metrics CRUD Operations
def create_performance_metric(db: Session, metric_data: PerformanceMetricsCreate) -> PerformanceMetricsOut:
    """Create performance metric"""
    db_metric = PerformanceMetrics(**metric_data.dict())
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return PerformanceMetricsOut.from_orm(db_metric)


def get_performance_metrics(
    db: Session,
    start_date: datetime,
    end_date: datetime,
    metric_type: Optional[str] = None,
    metric_name: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[PerformanceMetricsOut], int]:
    """Get performance metrics for date range"""
    query = db.query(PerformanceMetrics).filter(
        PerformanceMetrics.timestamp >= start_date,
        PerformanceMetrics.timestamp <= end_date
    )
    
    if metric_type:
        query = query.filter(PerformanceMetrics.metric_type == metric_type)
    if metric_name:
        query = query.filter(PerformanceMetrics.metric_name == metric_name)
    
    total = query.count()
    metrics = query.order_by(desc(PerformanceMetrics.timestamp)).offset(skip).limit(limit).all()
    
    return [PerformanceMetricsOut.from_orm(metric) for metric in metrics], total


def calculate_performance_summary(db: Session, start_date: datetime, end_date: datetime) -> PerformanceSummary:
    """Calculate performance summary"""
    # Calculate average response time
    avg_response_time = db.query(func.avg(PerformanceMetrics.metric_value)).filter(
        PerformanceMetrics.metric_type == "api",
        PerformanceMetrics.metric_name == "response_time",
        PerformanceMetrics.timestamp >= start_date,
        PerformanceMetrics.timestamp <= end_date
    ).scalar() or 0.0
    
    # Calculate requests per second
    total_requests = db.query(func.count(PerformanceMetrics.id)).filter(
        PerformanceMetrics.metric_type == "api",
        PerformanceMetrics.timestamp >= start_date,
        PerformanceMetrics.timestamp <= end_date
    ).scalar() or 0
    
    duration_seconds = (end_date - start_date).total_seconds()
    requests_per_second = total_requests / duration_seconds if duration_seconds > 0 else 0
    
    # Calculate error rate
    total_errors = db.query(func.count(PerformanceMetrics.id)).filter(
        PerformanceMetrics.metric_type == "api",
        PerformanceMetrics.metric_name == "error_count",
        PerformanceMetrics.timestamp >= start_date,
        PerformanceMetrics.timestamp <= end_date
    ).scalar() or 0
    
    error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
    
    # Get active users (from analytics events)
    active_users = db.query(func.count(func.distinct(AnalyticsEvent.user_id))).filter(
        AnalyticsEvent.created_at >= start_date,
        AnalyticsEvent.created_at <= end_date,
        AnalyticsEvent.user_id.isnot(None)
    ).scalar() or 0
    
    return PerformanceSummary(
        avg_response_time_ms=avg_response_time,
        requests_per_second=requests_per_second,
        error_rate=error_rate,
        uptime_percentage=100.0 - error_rate,  # Simplified calculation
        active_users=active_users,
        system_load=0.0,  # Would need system metrics
        date_range={"start": start_date, "end": end_date}
    )


# Report Template CRUD Operations
def create_report_template(db: Session, template_data: ReportTemplateCreate) -> ReportTemplateOut:
    """Create report template"""
    db_template = ReportTemplate(**template_data.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return ReportTemplateOut.from_orm(db_template)


def get_report_template(db: Session, template_id: int) -> Optional[ReportTemplateOut]:
    """Get report template by ID"""
    db_template = db.query(ReportTemplate).filter(ReportTemplate.id == template_id).first()
    return ReportTemplateOut.from_orm(db_template) if db_template else None


def get_report_templates(
    db: Session,
    report_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[ReportTemplateOut], int]:
    """Get report templates with filtering"""
    query = db.query(ReportTemplate)
    
    if report_type:
        query = query.filter(ReportTemplate.report_type == report_type)
    if is_active is not None:
        query = query.filter(ReportTemplate.is_active == is_active)
    
    total = query.count()
    templates = query.offset(skip).limit(limit).all()
    
    return [ReportTemplateOut.from_orm(template) for template in templates], total


def update_report_template(db: Session, template_id: int, template_data: ReportTemplateUpdate) -> Optional[ReportTemplateOut]:
    """Update report template"""
    db_template = db.query(ReportTemplate).filter(ReportTemplate.id == template_id).first()
    if not db_template:
        return None
    
    for field, value in template_data.dict(exclude_unset=True).items():
        setattr(db_template, field, value)
    
    db.commit()
    db.refresh(db_template)
    return ReportTemplateOut.from_orm(db_template)


def delete_report_template(db: Session, template_id: int) -> bool:
    """Delete report template"""
    db_template = db.query(ReportTemplate).filter(ReportTemplate.id == template_id).first()
    if not db_template:
        return False
    
    db.delete(db_template)
    db.commit()
    return True


# Scheduled Report CRUD Operations
def create_scheduled_report(db: Session, report_data: ScheduledReportCreate) -> ScheduledReportOut:
    """Create scheduled report"""
    db_report = ScheduledReport(**report_data.dict())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return ScheduledReportOut.from_orm(db_report)


def get_scheduled_reports(
    db: Session,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[ScheduledReportOut], int]:
    """Get scheduled reports"""
    query = db.query(ScheduledReport)
    
    if is_active is not None:
        query = query.filter(ScheduledReport.is_active == is_active)
    
    total = query.count()
    reports = query.order_by(desc(ScheduledReport.created_at)).offset(skip).limit(limit).all()
    
    return [ScheduledReportOut.from_orm(report) for report in reports], total


def update_scheduled_report(db: Session, report_id: int, report_data: ScheduledReportUpdate) -> Optional[ScheduledReportOut]:
    """Update scheduled report"""
    db_report = db.query(ScheduledReport).filter(ScheduledReport.id == report_id).first()
    if not db_report:
        return None
    
    for field, value in report_data.dict(exclude_unset=True).items():
        setattr(db_report, field, value)
    
    db.commit()
    db.refresh(db_report)
    return ScheduledReportOut.from_orm(db_report)


def delete_scheduled_report(db: Session, report_id: int) -> bool:
    """Delete scheduled report"""
    db_report = db.query(ScheduledReport).filter(ScheduledReport.id == report_id).first()
    if not db_report:
        return False
    
    db.delete(db_report)
    db.commit()
    return True


# Report Execution CRUD Operations
def create_report_execution(db: Session, execution_data: ReportExecutionCreate) -> ReportExecutionOut:
    """Create report execution"""
    db_execution = ReportExecution(**execution_data.dict())
    db.add(db_execution)
    db.commit()
    db.refresh(db_execution)
    return ReportExecutionOut.from_orm(db_execution)


def get_report_execution(db: Session, execution_id: int) -> Optional[ReportExecutionOut]:
    """Get report execution by ID"""
    db_execution = db.query(ReportExecution).filter(ReportExecution.id == execution_id).first()
    return ReportExecutionOut.from_orm(db_execution) if db_execution else None


def update_report_execution(db: Session, execution_id: int, **kwargs) -> Optional[ReportExecutionOut]:
    """Update report execution"""
    db_execution = db.query(ReportExecution).filter(ReportExecution.id == execution_id).first()
    if not db_execution:
        return None
    
    for field, value in kwargs.items():
        if hasattr(db_execution, field):
            setattr(db_execution, field, value)
    
    db.commit()
    db.refresh(db_execution)
    return ReportExecutionOut.from_orm(db_execution)


def generate_report(db: Session, request: ReportGenerationRequest) -> ReportGenerationResponse:
    """Generate a report"""
    # Create execution record
    execution_data = ReportExecutionCreate(
        report_name=f"{request.report_type.value}_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        execution_type="manual",
        status="running"
    )
    
    execution = create_report_execution(db, execution_data)
    
    # This would trigger actual report generation in a background task
    # For now, just return the execution ID
    
    return ReportGenerationResponse(
        execution_id=execution.id,
        status="running",
        estimated_completion_time=300  # 5 minutes
    )


# Dashboard CRUD Operations
def create_dashboard(db: Session, dashboard_data: DashboardCreate) -> DashboardOut:
    """Create dashboard"""
    db_dashboard = Dashboard(**dashboard_data.dict())
    db.add(db_dashboard)
    db.commit()
    db.refresh(db_dashboard)
    return DashboardOut.from_orm(db_dashboard)


def get_dashboard(db: Session, dashboard_id: int) -> Optional[DashboardOut]:
    """Get dashboard by ID"""
    db_dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    return DashboardOut.from_orm(db_dashboard) if db_dashboard else None


def get_user_dashboards(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[DashboardOut], int]:
    """Get user dashboards"""
    query = db.query(Dashboard).filter(Dashboard.user_id == user_id)
    
    total = query.count()
    dashboards = query.order_by(desc(Dashboard.created_at)).offset(skip).limit(limit).all()
    
    return [DashboardOut.from_orm(dashboard) for dashboard in dashboards], total


def update_dashboard(db: Session, dashboard_id: int, dashboard_data: DashboardUpdate) -> Optional[DashboardOut]:
    """Update dashboard"""
    db_dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not db_dashboard:
        return None
    
    for field, value in dashboard_data.dict(exclude_unset=True).items():
        setattr(db_dashboard, field, value)
    
    db.commit()
    db.refresh(db_dashboard)
    return DashboardOut.from_orm(db_dashboard)


def delete_dashboard(db: Session, dashboard_id: int) -> bool:
    """Delete dashboard"""
    db_dashboard = db.query(Dashboard).filter(Dashboard.id == dashboard_id).first()
    if not db_dashboard:
        return False
    
    db.delete(db_dashboard)
    db.commit()
    return True


# Data Export CRUD Operations
def create_data_export(db: Session, export_data: DataExportCreate) -> DataExportOut:
    """Create data export request"""
    db_export = DataExport(**export_data.dict())
    db.add(db_export)
    db.commit()
    db.refresh(db_export)
    return DataExportOut.from_orm(db_export)


def get_data_export(db: Session, export_id: int) -> Optional[DataExportOut]:
    """Get data export by ID"""
    db_export = db.query(DataExport).filter(DataExport.id == export_id).first()
    return DataExportOut.from_orm(db_export) if db_export else None


def update_data_export(db: Session, export_id: int, **kwargs) -> Optional[DataExportOut]:
    """Update data export"""
    db_export = db.query(DataExport).filter(DataExport.id == export_id).first()
    if not db_export:
        return None
    
    for field, value in kwargs.items():
        if hasattr(db_export, field):
            setattr(db_export, field, value)
    
    db.commit()
    db.refresh(db_export)
    return DataExportOut.from_orm(db_export)


def get_user_exports(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[DataExportOut], int]:
    """Get user data exports"""
    query = db.query(DataExport).filter(DataExport.user_id == user_id)
    
    total = query.count()
    exports = query.order_by(desc(DataExport.created_at)).offset(skip).limit(limit).all()
    
    return [DataExportOut.from_orm(export) for export in exports], total


# Real-time Analytics
def get_real_time_metrics(db: Session) -> RealTimeMetrics:
    """Get real-time metrics"""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Active users (last 15 minutes)
    active_users = db.query(func.count(func.distinct(AnalyticsEvent.user_id))).filter(
        AnalyticsEvent.created_at >= now - timedelta(minutes=15),
        AnalyticsEvent.user_id.isnot(None)
    ).scalar() or 0
    
    # Current orders (today)
    current_orders = db.query(func.count(AnalyticsEvent.id)).filter(
        AnalyticsEvent.event_type == "order_create",
        AnalyticsEvent.created_at >= today_start
    ).scalar() or 0
    
    # Revenue today (from business metrics)
    today_revenue = db.query(func.sum(BusinessMetrics.total_revenue)).filter(
        BusinessMetrics.date >= today_start
    ).scalar() or Decimal('0')
    
    # System performance (from performance metrics)
    avg_response_time = db.query(func.avg(PerformanceMetrics.metric_value)).filter(
        PerformanceMetrics.metric_type == "api",
        PerformanceMetrics.metric_name == "response_time",
        PerformanceMetrics.timestamp >= now - timedelta(minutes=5)
    ).scalar() or 0.0
    
    return RealTimeMetrics(
        active_users=active_users,
        current_orders=current_orders,
        revenue_today=today_revenue,
        system_performance={
            "avg_response_time_ms": avg_response_time,
            "requests_per_second": 0.0,  # Would need real-time calculation
            "error_rate": 0.0  # Would need real-time calculation
        },
        last_updated=now
    )


# Utility Functions
def track_event(
    db: Session,
    event_type: AnalyticsEventType,
    event_name: str,
    user_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    event_data: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> AnalyticsEventOut:
    """Track an analytics event"""
    event_data = AnalyticsEventCreate(
        event_type=event_type,
        event_name=event_name,
        user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        event_data=event_data,
        session_id=session_id,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return create_analytics_event(db, event_data)


def calculate_daily_metrics(db: Session, date: datetime) -> BusinessMetricsOut:
    """Calculate daily business metrics"""
    start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=1)
    
    # Calculate user metrics
    total_users = db.query(func.count(AnalyticsEvent.user_id.distinct())).filter(
        AnalyticsEvent.event_type == "user_registration",
        AnalyticsEvent.created_at < end_date
    ).scalar() or 0
    
    new_users = db.query(func.count(AnalyticsEvent.user_id.distinct())).filter(
        AnalyticsEvent.event_type == "user_registration",
        AnalyticsEvent.created_at >= start_date,
        AnalyticsEvent.created_at < end_date
    ).scalar() or 0
    
    active_users = db.query(func.count(AnalyticsEvent.user_id.distinct())).filter(
        AnalyticsEvent.created_at >= start_date,
        AnalyticsEvent.created_at < end_date,
        AnalyticsEvent.user_id.isnot(None)
    ).scalar() or 0
    
    # Calculate order metrics
    total_orders = db.query(func.count(AnalyticsEvent.id)).filter(
        AnalyticsEvent.event_type == "order_create",
        AnalyticsEvent.created_at >= start_date,
        AnalyticsEvent.created_at < end_date
    ).scalar() or 0
    
    # This is a simplified calculation - in production, you'd get actual order data
    order_value = Decimal('0')
    avg_order_value = Decimal('0')
    
    metrics_data = BusinessMetricsCreate(
        date=start_date,
        total_users=total_users,
        new_users=new_users,
        active_users=active_users,
        total_orders=total_orders,
        order_value=order_value,
        avg_order_value=avg_order_value
    )
    
    return create_business_metrics(db, metrics_data)


def cleanup_old_analytics(db: Session, days: int = 90) -> int:
    """Clean up old analytics data"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Delete old analytics events
    deleted_events = db.query(AnalyticsEvent).filter(
        AnalyticsEvent.created_at < cutoff_date
    ).delete()
    
    # Delete old performance metrics
    deleted_metrics = db.query(PerformanceMetrics).filter(
        PerformanceMetrics.timestamp < cutoff_date
    ).delete()
    
    # Delete old data exports
    deleted_exports = db.query(DataExport).filter(
        DataExport.created_at < cutoff_date
    ).delete()
    
    db.commit()
    return deleted_events + deleted_metrics + deleted_exports
