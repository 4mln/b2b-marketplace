"""
Analytics & Reporting System Schemas
Comprehensive business intelligence and reporting for the B2B marketplace
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
from decimal import Decimal


class AnalyticsEventType(str, Enum):
    # User events
    USER_REGISTRATION = "user_registration"
    USER_LOGIN = "user_login"
    USER_PROFILE_UPDATE = "user_profile_update"
    USER_LOGOUT = "user_logout"
    
    # Marketplace events
    PRODUCT_VIEW = "product_view"
    PRODUCT_SEARCH = "product_search"
    PRODUCT_FAVORITE = "product_favorite"
    PRODUCT_SHARE = "product_share"
    
    # Seller events
    SELLER_REGISTRATION = "seller_registration"
    PRODUCT_CREATE = "product_create"
    PRODUCT_UPDATE = "product_update"
    PRODUCT_DELETE = "product_delete"
    STORE_VIEW = "store_view"
    
    # Transaction events
    RFQ_CREATE = "rfq_create"
    RFQ_VIEW = "rfq_view"
    QUOTE_SUBMIT = "quote_submit"
    QUOTE_ACCEPT = "quote_accept"
    QUOTE_REJECT = "quote_reject"
    ORDER_CREATE = "order_create"
    ORDER_UPDATE = "order_update"
    ORDER_CANCEL = "order_cancel"
    PAYMENT_PROCESS = "payment_process"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    
    # Communication events
    MESSAGE_SEND = "message_send"
    MESSAGE_READ = "message_read"
    NOTIFICATION_SEND = "notification_send"
    NOTIFICATION_READ = "notification_read"
    
    # Advertising events
    AD_VIEW = "ad_view"
    AD_CLICK = "ad_click"
    AD_CONVERSION = "ad_conversion"
    CAMPAIGN_CREATE = "campaign_create"
    CAMPAIGN_UPDATE = "campaign_update"
    
    # System events
    SYSTEM_ERROR = "system_error"
    API_CALL = "api_call"
    PERFORMANCE_METRIC = "performance_metric"


class ReportType(str, Enum):
    BUSINESS = "business"
    USER = "user"
    SELLER = "seller"
    PRODUCT = "product"
    FINANCIAL = "financial"
    PERFORMANCE = "performance"
    CUSTOM = "custom"


class ExportFormat(str, Enum):
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    PDF = "pdf"


class ScheduleType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class ChartType(str, Enum):
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    DOUGHNUT = "doughnut"
    AREA = "area"
    SCATTER = "scatter"
    TABLE = "table"
    METRIC = "metric"


# Analytics Event Schemas
class AnalyticsEventBase(BaseModel):
    event_type: AnalyticsEventType
    event_name: str = Field(..., min_length=1, max_length=100)
    event_data: Optional[Dict[str, Any]] = None
    entity_type: Optional[str] = Field(None, max_length=50)
    entity_id: Optional[int] = None
    session_id: Optional[str] = Field(None, max_length=255)
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = None
    country: Optional[str] = Field(None, max_length=2)
    city: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class AnalyticsEventCreate(AnalyticsEventBase):
    user_id: Optional[int] = None


class AnalyticsEventOut(AnalyticsEventBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes = True


# Business Metrics Schemas
)
class BusinessMetricsBase(BaseModel):
    date: datetime
    
    # User metrics
    total_users: int = 0
    new_users: int = 0
    active_users: int = 0
    returning_users: int = 0
    user_growth_rate: float = 0.0
    
    # Seller metrics
    total_sellers: int = 0
    new_sellers: int = 0
    active_sellers: int = 0
    verified_sellers: int = 0
    
    # Product metrics
    total_products: int = 0
    new_products: int = 0
    active_products: int = 0
    featured_products: int = 0
    
    # Transaction metrics
    total_orders: int = 0
    new_orders: int = 0
    completed_orders: int = 0
    cancelled_orders: int = 0
    order_value: Decimal = Decimal('0')
    avg_order_value: Decimal = Decimal('0')
    
    # RFQ metrics
    total_rfqs: int = 0
    new_rfqs: int = 0
    completed_rfqs: int = 0
    avg_quotes_per_rfq: float = 0.0
    
    # Financial metrics
    total_revenue: Decimal = Decimal('0')
    total_transactions: int = 0
    avg_transaction_value: Decimal = Decimal('0')
    commission_earned: Decimal = Decimal('0')
    
    # Engagement metrics
    total_page_views: int = 0
    unique_page_views: int = 0
    avg_session_duration: float = 0.0
    bounce_rate: float = 0.0


class BusinessMetricsCreate(BusinessMetricsBase):
    pass


class BusinessMetricsOut(BusinessMetricsBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes = True


# User Analytics Schemas
)
class UserAnalyticsBase(BaseModel):
    date: datetime
    
    # Session metrics
    sessions_count: int = 0
    total_session_duration: float = 0.0
    avg_session_duration: float = 0.0
    
    # Page view metrics
    page_views_count: int = 0
    unique_page_views: int = 0
    pages_per_session: float = 0.0
    
    # Search metrics
    searches_count: int = 0
    unique_searches: int = 0
    search_results_clicked: int = 0
    search_conversion_rate: float = 0.0
    
    # Product interaction metrics
    products_viewed: int = 0
    products_favorited: int = 0
    products_shared: int = 0
    
    # Transaction metrics
    orders_placed: int = 0
    orders_completed: int = 0
    orders_cancelled: int = 0
    total_spent: Decimal = Decimal('0')
    avg_order_value: Decimal = Decimal('0')
    
    # Communication metrics
    messages_sent: int = 0
    messages_received: int = 0
    notifications_received: int = 0
    notifications_read: int = 0


class UserAnalyticsCreate(UserAnalyticsBase):
    user_id: int


class UserAnalyticsOut(UserAnalyticsBase):
    id: int
    user_id: int
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes = True


# Seller Analytics Schemas
)
class SellerAnalyticsBase(BaseModel):
    date: datetime
    
    # Store metrics
    store_views: int = 0
    unique_store_visitors: int = 0
    store_favorites: int = 0
    
    # Product metrics
    total_products: int = 0
    active_products: int = 0
    featured_products: int = 0
    product_views: int = 0
    product_favorites: int = 0
    product_shares: int = 0
    
    # Order metrics
    orders_received: int = 0
    orders_completed: int = 0
    orders_cancelled: int = 0
    total_revenue: Decimal = Decimal('0')
    avg_order_value: Decimal = Decimal('0')
    
    # RFQ metrics
    rfqs_received: int = 0
    quotes_submitted: int = 0
    quotes_accepted: int = 0
    quote_acceptance_rate: float = 0.0
    
    # Communication metrics
    messages_received: int = 0
    messages_responded: int = 0
    avg_response_time: float = 0.0
    
    # Rating metrics
    total_ratings: int = 0
    avg_rating: float = 0.0
    positive_ratings: int = 0
    negative_ratings: int = 0


class SellerAnalyticsCreate(SellerAnalyticsBase):
    seller_id: int


class SellerAnalyticsOut(SellerAnalyticsBase):
    id: int
    seller_id: int
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes = True


# Product Analytics Schemas
)
class ProductAnalyticsBase(BaseModel):
    date: datetime
    
    # View metrics
    views_count: int = 0
    unique_views: int = 0
    views_from_search: int = 0
    views_from_category: int = 0
    views_from_recommendations: int = 0
    
    # Interaction metrics
    favorites_count: int = 0
    shares_count: int = 0
    inquiries_count: int = 0
    
    # Conversion metrics
    orders_count: int = 0
    revenue_generated: Decimal = Decimal('0')
    conversion_rate: float = 0.0
    
    # Search metrics
    search_impressions: int = 0
    search_clicks: int = 0
    search_click_through_rate: float = 0.0
    search_position: float = 0.0


class ProductAnalyticsCreate(ProductAnalyticsBase):
    product_id: int


class ProductAnalyticsOut(ProductAnalyticsBase):
    id: int
    product_id: int
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes = True


# Financial Report Schemas
)
class FinancialReportBase(BaseModel):
    report_date: datetime
    report_type: str = Field(..., max_length=50)
    
    # Revenue metrics
    gross_revenue: Decimal = Decimal('0')
    net_revenue: Decimal = Decimal('0')
    commission_revenue: Decimal = Decimal('0')
    subscription_revenue: Decimal = Decimal('0')
    advertising_revenue: Decimal = Decimal('0')
    
    # Transaction metrics
    total_transactions: int = 0
    successful_transactions: int = 0
    failed_transactions: int = 0
    avg_transaction_value: Decimal = Decimal('0')
    
    # Payment metrics
    total_payments_processed: Decimal = Decimal('0')
    payment_success_rate: float = 0.0
    refund_amount: Decimal = Decimal('0')
    chargeback_amount: Decimal = Decimal('0')
    
    # Cost metrics
    operational_costs: Decimal = Decimal('0')
    marketing_costs: Decimal = Decimal('0')
    technology_costs: Decimal = Decimal('0')
    total_costs: Decimal = Decimal('0')
    
    # Profitability metrics
    gross_profit: Decimal = Decimal('0')
    net_profit: Decimal = Decimal('0')
    profit_margin: float = 0.0


class FinancialReportCreate(FinancialReportBase):
    pass


class FinancialReportOut(FinancialReportBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes = True


# Performance Metrics Schemas
)
class PerformanceMetricsBase(BaseModel):
    timestamp: datetime
    metric_type: str = Field(..., max_length=50)
    metric_name: str = Field(..., min_length=1, max_length=100)
    metric_value: float
    metric_unit: Optional[str] = Field(None, max_length=20)
    endpoint: Optional[str] = Field(None, max_length=200)
    method: Optional[str] = Field(None, max_length=10)
    status_code: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class PerformanceMetricsCreate(PerformanceMetricsBase):
    user_id: Optional[int] = None


class PerformanceMetricsOut(PerformanceMetricsBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes = True


# Report Template Schemas
)
class ReportTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    report_type: ReportType
    template_config: Dict[str, Any]
    schedule_config: Optional[Dict[str, Any]] = None
    export_config: Optional[Dict[str, Any]] = None
    is_public: bool = False
    allowed_roles: Optional[List[str]] = None
    is_active: bool = True


class ReportTemplateCreate(ReportTemplateBase):
    pass


class ReportTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    template_config: Optional[Dict[str, Any]] = None
    schedule_config: Optional[Dict[str, Any]] = None
    export_config: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None
    allowed_roles: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ReportTemplateOut(ReportTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes = True


# Scheduled Report Schemas
)
class ScheduledReportBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    template_id: Optional[int] = None
    schedule_type: ScheduleType
    schedule_config: Dict[str, Any]
    timezone: Optional[str] = Field(None, max_length=50)
    recipients: List[Union[str, int]]  # emails or user IDs
    delivery_method: str = "email"
    is_active: bool = True


class ScheduledReportCreate(ScheduledReportBase):
    pass


class ScheduledReportUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    schedule_config: Optional[Dict[str, Any]] = None
    timezone: Optional[str] = Field(None, max_length=50)
    recipients: Optional[List[Union[str, int]]] = None
    delivery_method: Optional[str] = None
    is_active: Optional[bool] = None


class ScheduledReportOut(ScheduledReportBase):
    id: int
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes = True


# Report Execution Schemas
)
class ReportExecutionBase(BaseModel):
    report_name: str = Field(..., min_length=1, max_length=255)
    execution_type: str = Field(..., max_length=20)
    status: str = Field(..., max_length=20)
    parameters: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    result_data: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = Field(None, max_length=500)
    file_size: Optional[int] = None
    execution_time_ms: Optional[int] = None
    rows_processed: Optional[int] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None


class ReportExecutionCreate(ReportExecutionBase):
    scheduled_report_id: Optional[int] = None


class ReportExecutionOut(ReportExecutionBase):
    id: int
    scheduled_report_id: Optional[int] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        from_attributes = True


# Dashboard Schemas
)
class DashboardBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_default: bool = False
    layout_config: Dict[str, Any]
    widget_config: Dict[str, Any]
    filters_config: Optional[Dict[str, Any]] = None
    is_public: bool = False
    shared_with: Optional[List[int]] = None


class DashboardCreate(DashboardBase):
    user_id: int


class DashboardUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_default: Optional[bool] = None
    layout_config: Optional[Dict[str, Any]] = None
    widget_config: Optional[Dict[str, Any]] = None
    filters_config: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None
    shared_with: Optional[List[int]] = None


class DashboardOut(DashboardBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes = True


# Data Export Schemas
)
class DataExportBase(BaseModel):
    export_type: str = Field(..., max_length=50)
    export_format: ExportFormat
    file_name: str = Field(..., min_length=1, max_length=255)
    filters: Optional[Dict[str, Any]] = None
    columns: Optional[List[str]] = None
    date_range: Optional[Dict[str, Any]] = None
    status: str = "pending"
    progress: float = 0.0
    file_path: Optional[str] = Field(None, max_length=500)
    file_size: Optional[int] = None
    download_count: int = 0
    processing_time_ms: Optional[int] = None
    rows_exported: Optional[int] = None
    error_message: Optional[str] = None


class DataExportCreate(DataExportBase):
    user_id: int


class DataExportOut(DataExportBase):
    id: int
    user_id: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        from_attributes = True


# Request/Response Schemas
)
class AnalyticsEventListResponse(BaseModel):
    events: List[AnalyticsEventOut]
    total: int
    page: int
    page_size: int


class BusinessMetricsListResponse(BaseModel):
    metrics: List[BusinessMetricsOut]
    total: int
    page: int
    page_size: int


class UserAnalyticsListResponse(BaseModel):
    analytics: List[UserAnalyticsOut]
    total: int
    page: int
    page_size: int


class SellerAnalyticsListResponse(BaseModel):
    analytics: List[SellerAnalyticsOut]
    total: int
    page: int
    page_size: int


class ProductAnalyticsListResponse(BaseModel):
    analytics: List[ProductAnalyticsOut]
    total: int
    page: int
    page_size: int


class FinancialReportListResponse(BaseModel):
    reports: List[FinancialReportOut]
    total: int
    page: int
    page_size: int


class PerformanceMetricsListResponse(BaseModel):
    metrics: List[PerformanceMetricsOut]
    total: int
    page: int
    page_size: int


class ReportTemplateListResponse(BaseModel):
    templates: List[ReportTemplateOut]
    total: int
    page: int
    page_size: int


class ScheduledReportListResponse(BaseModel):
    reports: List[ScheduledReportOut]
    total: int
    page: int
    page_size: int


class ReportExecutionListResponse(BaseModel):
    executions: List[ReportExecutionOut]
    total: int
    page: int
    page_size: int


class DashboardListResponse(BaseModel):
    dashboards: List[DashboardOut]
    total: int
    page: int
    page_size: int


class DataExportListResponse(BaseModel):
    exports: List[DataExportOut]
    total: int
    page: int
    page_size: int


# Advanced Analytics Schemas
class AnalyticsQueryRequest(BaseModel):
    event_types: Optional[List[AnalyticsEventType]] = None
    entity_types: Optional[List[str]] = None
    user_ids: Optional[List[int]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    group_by: Optional[List[str]] = None
    metrics: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None
    limit: int = Field(100, ge=1, le=1000)


class AnalyticsQueryResponse(BaseModel):
    results: List[Dict[str, Any]]
    total: int
    query_time_ms: int
    metadata: Optional[Dict[str, Any]] = None


class BusinessMetricsSummary(BaseModel):
    total_users: int
    total_sellers: int
    total_products: int
    total_orders: int
    total_revenue: Decimal
    avg_order_value: Decimal
    user_growth_rate: float
    revenue_growth_rate: float
    date_range: Dict[str, datetime]


class PerformanceSummary(BaseModel):
    avg_response_time_ms: float
    requests_per_second: float
    error_rate: float
    uptime_percentage: float
    active_users: int
    system_load: float
    date_range: Dict[str, datetime]


class ReportGenerationRequest(BaseModel):
    template_id: Optional[int] = None
    report_type: ReportType
    parameters: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    date_range: Optional[Dict[str, datetime]] = None
    export_format: Optional[ExportFormat] = None


class ReportGenerationResponse(BaseModel):
    execution_id: int
    status: str
    estimated_completion_time: Optional[int] = None
    download_url: Optional[str] = None


class DashboardWidget(BaseModel):
    id: str
    type: ChartType
    title: str
    description: Optional[str] = None
    config: Dict[str, Any]
    data_source: str
    refresh_interval: Optional[int] = None  # in seconds


class DashboardLayout(BaseModel):
    widgets: List[DashboardWidget]
    layout: Dict[str, Any]
    filters: Optional[Dict[str, Any]] = None


class AnalyticsFilter(BaseModel):
    field: str
    operator: str  # eq, gt, lt, in, contains, etc.
    value: Any
    logical_operator: Optional[str] = None  # AND, OR


class AnalyticsRequest(BaseModel):
    filters: Optional[List[AnalyticsFilter]] = None
    date_range: Optional[Dict[str, datetime]] = None
    group_by: Optional[List[str]] = None
    metrics: Optional[List[str]] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


class AnalyticsResponse(BaseModel):
    data: List[Dict[str, Any]]
    total: int
    query_time_ms: int
    metadata: Optional[Dict[str, Any]] = None


# Real-time Analytics Schemas
class RealTimeMetrics(BaseModel):
    active_users: int
    current_orders: int
    revenue_today: Decimal
    system_performance: Dict[str, float]
    last_updated: datetime


class AnalyticsAlert(BaseModel):
    id: int
    alert_type: str
    title: str
    message: str
    severity: str  # low, medium, high, critical
    metric_name: str
    threshold_value: float
    current_value: float
    triggered_at: datetime
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None