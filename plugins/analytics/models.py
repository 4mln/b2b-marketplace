"""
Analytics & Reporting System Models
Comprehensive business intelligence and reporting for the B2B marketplace
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float, Index, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.db.base import Base


class AnalyticsEventType(str, enum.Enum):
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


class AnalyticsEvent(Base):
    """Analytics events tracking"""
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True, index=True)
    
    # Event details
    event_type = Column(String(50), nullable=False)
    event_name = Column(String(100), nullable=False)
    event_data = Column(JSON, nullable=True)  # Additional event data
    
    # User context
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(255), nullable=True)
    
    # Entity context
    entity_type = Column(String(50), nullable=True)  # product, seller, order, etc.
    entity_id = Column(Integer, nullable=True)
    
    # Location and device
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    country = Column(String(2), nullable=True)
    city = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")


class BusinessMetrics(Base):
    """Business performance metrics"""
    __tablename__ = "business_metrics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False)
    
    # User metrics
    total_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    returning_users = Column(Integer, default=0)
    user_growth_rate = Column(Float, default=0.0)
    
    # Seller metrics
    total_sellers = Column(Integer, default=0)
    new_sellers = Column(Integer, default=0)
    active_sellers = Column(Integer, default=0)
    verified_sellers = Column(Integer, default=0)
    
    # Product metrics
    total_products = Column(Integer, default=0)
    new_products = Column(Integer, default=0)
    active_products = Column(Integer, default=0)
    featured_products = Column(Integer, default=0)
    
    # Transaction metrics
    total_orders = Column(Integer, default=0)
    new_orders = Column(Integer, default=0)
    completed_orders = Column(Integer, default=0)
    cancelled_orders = Column(Integer, default=0)
    order_value = Column(Numeric(15, 2), default=0)
    avg_order_value = Column(Numeric(15, 2), default=0)
    
    # RFQ metrics
    total_rfqs = Column(Integer, default=0)
    new_rfqs = Column(Integer, default=0)
    completed_rfqs = Column(Integer, default=0)
    avg_quotes_per_rfq = Column(Float, default=0.0)
    
    # Financial metrics
    total_revenue = Column(Numeric(15, 2), default=0)
    total_transactions = Column(Integer, default=0)
    avg_transaction_value = Column(Numeric(15, 2), default=0)
    commission_earned = Column(Numeric(15, 2), default=0)
    
    # Engagement metrics
    total_page_views = Column(Integer, default=0)
    unique_page_views = Column(Integer, default=0)
    avg_session_duration = Column(Float, default=0.0)
    bounce_rate = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserAnalytics(Base):
    """User behavior analytics"""
    __tablename__ = "user_analytics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    
    # Session metrics
    sessions_count = Column(Integer, default=0)
    total_session_duration = Column(Float, default=0.0)
    avg_session_duration = Column(Float, default=0.0)
    
    # Page view metrics
    page_views_count = Column(Integer, default=0)
    unique_page_views = Column(Integer, default=0)
    pages_per_session = Column(Float, default=0.0)
    
    # Search metrics
    searches_count = Column(Integer, default=0)
    unique_searches = Column(Integer, default=0)
    search_results_clicked = Column(Integer, default=0)
    search_conversion_rate = Column(Float, default=0.0)
    
    # Product interaction metrics
    products_viewed = Column(Integer, default=0)
    products_favorited = Column(Integer, default=0)
    products_shared = Column(Integer, default=0)
    
    # Transaction metrics
    orders_placed = Column(Integer, default=0)
    orders_completed = Column(Integer, default=0)
    orders_cancelled = Column(Integer, default=0)
    total_spent = Column(Numeric(15, 2), default=0)
    avg_order_value = Column(Numeric(15, 2), default=0)
    
    # Communication metrics
    messages_sent = Column(Integer, default=0)
    messages_received = Column(Integer, default=0)
    notifications_received = Column(Integer, default=0)
    notifications_read = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")


class SellerAnalytics(Base):
    """Seller performance analytics"""
    __tablename__ = "seller_analytics"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    
    # Store metrics
    store_views = Column(Integer, default=0)
    unique_store_visitors = Column(Integer, default=0)
    store_favorites = Column(Integer, default=0)
    
    # Product metrics
    total_products = Column(Integer, default=0)
    active_products = Column(Integer, default=0)
    featured_products = Column(Integer, default=0)
    product_views = Column(Integer, default=0)
    product_favorites = Column(Integer, default=0)
    product_shares = Column(Integer, default=0)
    
    # Order metrics
    orders_received = Column(Integer, default=0)
    orders_completed = Column(Integer, default=0)
    orders_cancelled = Column(Integer, default=0)
    total_revenue = Column(Numeric(15, 2), default=0)
    avg_order_value = Column(Numeric(15, 2), default=0)
    
    # RFQ metrics
    rfqs_received = Column(Integer, default=0)
    quotes_submitted = Column(Integer, default=0)
    quotes_accepted = Column(Integer, default=0)
    quote_acceptance_rate = Column(Float, default=0.0)
    
    # Communication metrics
    messages_received = Column(Integer, default=0)
    messages_responded = Column(Integer, default=0)
    avg_response_time = Column(Float, default=0.0)  # in minutes
    
    # Rating metrics
    total_ratings = Column(Integer, default=0)
    avg_rating = Column(Float, default=0.0)
    positive_ratings = Column(Integer, default=0)
    negative_ratings = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    seller = relationship("Seller")


class ProductAnalytics(Base):
    """Product performance analytics"""
    __tablename__ = "product_analytics"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    
    # View metrics
    views_count = Column(Integer, default=0)
    unique_views = Column(Integer, default=0)
    views_from_search = Column(Integer, default=0)
    views_from_category = Column(Integer, default=0)
    views_from_recommendations = Column(Integer, default=0)
    
    # Interaction metrics
    favorites_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    inquiries_count = Column(Integer, default=0)
    
    # Conversion metrics
    orders_count = Column(Integer, default=0)
    revenue_generated = Column(Numeric(15, 2), default=0)
    conversion_rate = Column(Float, default=0.0)
    
    # Search metrics
    search_impressions = Column(Integer, default=0)
    search_clicks = Column(Integer, default=0)
    search_click_through_rate = Column(Float, default=0.0)
    search_position = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    product = relationship("Product")


class FinancialReport(Base):
    """Financial reporting and analysis"""
    __tablename__ = "financial_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_date = Column(DateTime(timezone=True), nullable=False)
    report_type = Column(String(50), nullable=False)  # daily, weekly, monthly, yearly
    
    # Revenue metrics
    gross_revenue = Column(Numeric(15, 2), default=0)
    net_revenue = Column(Numeric(15, 2), default=0)
    commission_revenue = Column(Numeric(15, 2), default=0)
    subscription_revenue = Column(Numeric(15, 2), default=0)
    advertising_revenue = Column(Numeric(15, 2), default=0)
    
    # Transaction metrics
    total_transactions = Column(Integer, default=0)
    successful_transactions = Column(Integer, default=0)
    failed_transactions = Column(Integer, default=0)
    avg_transaction_value = Column(Numeric(15, 2), default=0)
    
    # Payment metrics
    total_payments_processed = Column(Numeric(15, 2), default=0)
    payment_success_rate = Column(Float, default=0.0)
    refund_amount = Column(Numeric(15, 2), default=0)
    chargeback_amount = Column(Numeric(15, 2), default=0)
    
    # Cost metrics
    operational_costs = Column(Numeric(15, 2), default=0)
    marketing_costs = Column(Numeric(15, 2), default=0)
    technology_costs = Column(Numeric(15, 2), default=0)
    total_costs = Column(Numeric(15, 2), default=0)
    
    # Profitability metrics
    gross_profit = Column(Numeric(15, 2), default=0)
    net_profit = Column(Numeric(15, 2), default=0)
    profit_margin = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PerformanceMetrics(Base):
    """System performance metrics"""
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    metric_type = Column(String(50), nullable=False)  # api, database, cache, etc.
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20), nullable=True)  # ms, %, count, etc.
    
    # Context
    endpoint = Column(String(200), nullable=True)
    method = Column(String(10), nullable=True)
    status_code = Column(Integer, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Additional data
    metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")


class ReportTemplate(Base):
    """Report templates for different types of reports"""
    __tablename__ = "report_templates"

    id = Column(Integer, primary_key=True, index=True)
    
    # Template details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(String(50), nullable=False)  # business, user, seller, financial, etc.
    
    # Configuration
    template_config = Column(JSON, nullable=False)  # Chart types, metrics, filters, etc.
    schedule_config = Column(JSON, nullable=True)  # Scheduling configuration
    export_config = Column(JSON, nullable=True)  # Export format configuration
    
    # Access control
    is_public = Column(Boolean, default=False)
    allowed_roles = Column(JSON, nullable=True)  # Array of allowed roles
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ScheduledReport(Base):
    """Scheduled reports for automated delivery"""
    __tablename__ = "scheduled_reports"

    id = Column(Integer, primary_key=True, index=True)
    
    # Report details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    template_id = Column(Integer, ForeignKey("report_templates.id"), nullable=True)
    
    # Schedule configuration
    schedule_type = Column(String(20), nullable=False)  # daily, weekly, monthly
    schedule_config = Column(JSON, nullable=False)  # Specific schedule details
    timezone = Column(String(50), nullable=True)
    
    # Recipients
    recipients = Column(JSON, nullable=False)  # Array of recipient emails/user IDs
    delivery_method = Column(String(20), default="email")  # email, webhook, etc.
    
    # Status
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    next_run_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    template = relationship("ReportTemplate")


class ReportExecution(Base):
    """Report execution history"""
    __tablename__ = "report_executions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Execution details
    report_name = Column(String(255), nullable=False)
    execution_type = Column(String(20), nullable=False)  # manual, scheduled
    status = Column(String(20), nullable=False)  # running, completed, failed
    
    # Configuration
    parameters = Column(JSON, nullable=True)  # Report parameters
    filters = Column(JSON, nullable=True)  # Applied filters
    
    # Results
    result_data = Column(JSON, nullable=True)  # Report results
    file_path = Column(String(500), nullable=True)  # Generated file path
    file_size = Column(Integer, nullable=True)  # File size in bytes
    
    # Performance
    execution_time_ms = Column(Integer, nullable=True)
    rows_processed = Column(Integer, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    stack_trace = Column(Text, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    scheduled_report_id = Column(Integer, ForeignKey("scheduled_reports.id"), nullable=True)
    scheduled_report = relationship("ScheduledReport")


class Dashboard(Base):
    """User dashboards for analytics visualization"""
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Dashboard details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False)
    
    # Configuration
    layout_config = Column(JSON, nullable=False)  # Dashboard layout
    widget_config = Column(JSON, nullable=False)  # Widget configurations
    filters_config = Column(JSON, nullable=True)  # Global filters
    
    # Access control
    is_public = Column(Boolean, default=False)
    shared_with = Column(JSON, nullable=True)  # Array of user IDs
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User")


class DataExport(Base):
    """Data export requests and history"""
    __tablename__ = "data_exports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Export details
    export_type = Column(String(50), nullable=False)  # analytics, reports, etc.
    export_format = Column(String(20), nullable=False)  # csv, excel, json, pdf
    file_name = Column(String(255), nullable=False)
    
    # Configuration
    filters = Column(JSON, nullable=True)  # Applied filters
    columns = Column(JSON, nullable=True)  # Selected columns
    date_range = Column(JSON, nullable=True)  # Date range configuration
    
    # Status
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    progress = Column(Float, default=0.0)  # Progress percentage
    
    # Results
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    download_count = Column(Integer, default=0)
    
    # Performance
    processing_time_ms = Column(Integer, nullable=True)
    rows_exported = Column(Integer, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User")


# Create indexes for better performance
Index('idx_analytics_events_type_date', AnalyticsEvent.event_type, AnalyticsEvent.created_at.desc())
Index('idx_analytics_events_user_date', AnalyticsEvent.user_id, AnalyticsEvent.created_at.desc())
Index('idx_analytics_events_entity', AnalyticsEvent.entity_type, AnalyticsEvent.entity_id)

Index('idx_business_metrics_date', BusinessMetrics.date)
Index('idx_business_metrics_type', BusinessMetrics.date.desc())

Index('idx_user_analytics_user_date', UserAnalytics.user_id, UserAnalytics.date)
Index('idx_user_analytics_date', UserAnalytics.date)

Index('idx_seller_analytics_seller_date', SellerAnalytics.seller_id, SellerAnalytics.date)
Index('idx_seller_analytics_date', SellerAnalytics.date)

Index('idx_product_analytics_product_date', ProductAnalytics.product_id, ProductAnalytics.date)
Index('idx_product_analytics_date', ProductAnalytics.date)

Index('idx_financial_reports_date_type', FinancialReport.report_date, FinancialReport.report_type)
Index('idx_financial_reports_date', FinancialReport.report_date.desc())

Index('idx_performance_metrics_timestamp_type', PerformanceMetrics.timestamp, PerformanceMetrics.metric_type)
Index('idx_performance_metrics_name', PerformanceMetrics.metric_name)

Index('idx_report_templates_type', ReportTemplate.report_type)
Index('idx_report_templates_active', ReportTemplate.is_active)

Index('idx_scheduled_reports_active', ScheduledReport.is_active)
Index('idx_scheduled_reports_next_run', ScheduledReport.next_run_at)

Index('idx_report_executions_status', ReportExecution.status)
Index('idx_report_executions_started', ReportExecution.started_at.desc())

Index('idx_dashboards_user', Dashboard.user_id)
Index('idx_dashboards_default', Dashboard.user_id, Dashboard.is_default)

Index('idx_data_exports_user_status', DataExport.user_id, DataExport.status)
Index('idx_data_exports_created', DataExport.created_at.desc())
