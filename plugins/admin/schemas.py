"""
Admin Dashboard System Schemas
Comprehensive administrative capabilities for the B2B marketplace
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class AdminActionType(str, Enum):
    USER_MANAGEMENT = "user_management"
    CONTENT_MODERATION = "content_moderation"
    PAYMENT_MANAGEMENT = "payment_management"
    AD_APPROVAL = "ad_approval"
    SYSTEM_CONFIG = "system_config"
    SECURITY = "security"
    ANALYTICS = "analytics"
    SUPPORT = "support"


class AdminActionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"


class AdminRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    SUPPORT = "support"
    ANALYST = "analyst"


class AdminPermission(str, Enum):
    # User Management
    VIEW_USERS = "view_users"
    EDIT_USERS = "edit_users"
    DELETE_USERS = "delete_users"
    SUSPEND_USERS = "suspend_users"
    VERIFY_KYC = "verify_kyc"
    
    # Content Moderation
    MODERATE_PRODUCTS = "moderate_products"
    MODERATE_REVIEWS = "moderate_reviews"
    MODERATE_MESSAGES = "moderate_messages"
    APPROVE_ADS = "approve_ads"
    
    # Payment Management
    VIEW_PAYMENTS = "view_payments"
    PROCESS_REFUNDS = "process_refunds"
    MANAGE_WALLETS = "manage_wallets"
    VIEW_FINANCIAL_REPORTS = "view_financial_reports"
    
    # System Configuration
    MANAGE_GUILDS = "manage_guilds"
    MANAGE_CATEGORIES = "manage_categories"
    CONFIGURE_SYSTEM = "configure_system"
    MANAGE_PLUGINS = "manage_plugins"
    
    # Security
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_SECURITY = "manage_security"
    BLOCK_IPS = "block_ips"
    
    # Analytics
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_DATA = "export_data"
    VIEW_REPORTS = "view_reports"
    
    # Support
    MANAGE_TICKETS = "manage_tickets"
    RESPOND_TO_SUPPORT = "respond_to_support"
    ESCALATE_ISSUES = "escalate_issues"


# Admin User Schemas
class AdminUserBase(BaseModel):
    role: AdminRole
    permissions: Optional[List[AdminPermission]] = None
    is_active: bool = True


class AdminUserCreate(AdminUserBase):
    user_id: int


class AdminUserUpdate(BaseModel):
    role: Optional[AdminRole] = None
    permissions: Optional[List[AdminPermission]] = None
    is_active: Optional[bool] = None


class AdminUserOut(AdminUserBase):
    id: int
    user_id: int
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Admin Action Schemas
class AdminActionBase(BaseModel):
    action_type: AdminActionType
    target_type: Optional[str] = None
    target_id: Optional[int] = None
    description: str
    details: Optional[Dict[str, Any]] = None


class AdminActionCreate(AdminActionBase):
    pass


class AdminActionUpdate(BaseModel):
    action_status: Optional[AdminActionStatus] = None
    details: Optional[Dict[str, Any]] = None


class AdminActionOut(AdminActionBase):
    id: int
    admin_user_id: int
    action_status: AdminActionStatus
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# System Config Schemas
class SystemConfigBase(BaseModel):
    key: str = Field(..., max_length=255)
    value: Optional[str] = None
    value_type: str = Field(..., max_length=50)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    is_public: bool = False


class SystemConfigCreate(SystemConfigBase):
    pass


class SystemConfigUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    is_public: Optional[bool] = None


class SystemConfigOut(SystemConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Audit Log Schemas
class AuditLogBase(BaseModel):
    event_type: str = Field(..., max_length=100)
    event_category: Optional[str] = Field(None, max_length=100)
    description: str
    details: Optional[Dict[str, Any]] = None
    target_type: Optional[str] = Field(None, max_length=100)
    target_id: Optional[int] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = None
    session_id: Optional[str] = Field(None, max_length=255)


class AuditLogCreate(AuditLogBase):
    user_id: Optional[int] = None
    admin_user_id: Optional[int] = None


class AuditLogOut(AuditLogBase):
    id: int
    user_id: Optional[int] = None
    admin_user_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Support Ticket Schemas
class SupportTicketBase(BaseModel):
    subject: str = Field(..., max_length=255)
    description: str
    category: str = Field(..., max_length=100)
    priority: str = Field(..., max_length=50)
    status: str = Field(..., max_length=50)


class SupportTicketCreate(SupportTicketBase):
    pass


class SupportTicketUpdate(BaseModel):
    subject: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    priority: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=50)
    assigned_admin_id: Optional[int] = None


class SupportTicketOut(SupportTicketBase):
    id: int
    user_id: int
    assigned_admin_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Support Message Schemas
class SupportMessageBase(BaseModel):
    content: str
    is_internal: bool = False


class SupportMessageCreate(SupportMessageBase):
    pass


class SupportMessageOut(SupportMessageBase):
    id: int
    ticket_id: int
    user_id: Optional[int] = None
    admin_user_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Content Moderation Schemas
class ContentModerationBase(BaseModel):
    content_type: str = Field(..., max_length=100)
    content_id: int
    reason: str = Field(..., max_length=255)
    description: Optional[str] = None
    status: str = Field(..., max_length=50)
    action_taken: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class ContentModerationCreate(ContentModerationBase):
    reported_by: Optional[int] = None


class ContentModerationUpdate(BaseModel):
    status: Optional[str] = Field(None, max_length=50)
    action_taken: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    assigned_admin_id: Optional[int] = None


class ContentModerationOut(ContentModerationBase):
    id: int
    reported_by: Optional[int] = None
    assigned_admin_id: Optional[int] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# System Metrics Schemas
class SystemMetricsBase(BaseModel):
    metric_name: str = Field(..., max_length=255)
    metric_value: float
    metric_unit: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    metadata: Optional[Dict[str, Any]] = None


class SystemMetricsCreate(SystemMetricsBase):
    pass


class SystemMetricsOut(SystemMetricsBase):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


# Admin Dashboard Schemas
class AdminDashboardBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    layout: Optional[Dict[str, Any]] = None
    widgets: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    is_default: bool = False
    is_public: bool = False


class AdminDashboardCreate(AdminDashboardBase):
    pass


class AdminDashboardUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    layout: Optional[Dict[str, Any]] = None
    widgets: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    is_default: Optional[bool] = None
    is_public: Optional[bool] = None


class AdminDashboardOut(AdminDashboardBase):
    id: int
    admin_user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Admin Notification Schemas
class AdminNotificationBase(BaseModel):
    title: str = Field(..., max_length=255)
    message: str
    notification_type: str = Field(..., max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    action_url: Optional[str] = Field(None, max_length=500)
    action_text: Optional[str] = Field(None, max_length=100)
    is_urgent: bool = False


class AdminNotificationCreate(AdminNotificationBase):
    pass


class AdminNotificationUpdate(BaseModel):
    is_read: Optional[bool] = None


class AdminNotificationOut(AdminNotificationBase):
    id: int
    admin_user_id: int
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# IP Blocklist Schemas
class IPBlocklistBase(BaseModel):
    ip_address: str = Field(..., max_length=45)
    reason: str
    block_type: str = Field(..., max_length=50)
    expires_at: Optional[datetime] = None


class IPBlocklistCreate(IPBlocklistBase):
    pass


class IPBlocklistUpdate(BaseModel):
    reason: Optional[str] = None
    block_type: Optional[str] = Field(None, max_length=50)
    expires_at: Optional[datetime] = None


class IPBlocklistOut(IPBlocklistBase):
    id: int
    added_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Admin Report Schemas
class AdminReportBase(BaseModel):
    report_name: str = Field(..., max_length=255)
    report_type: str = Field(..., max_length=100)
    parameters: Optional[Dict[str, Any]] = None


class AdminReportCreate(AdminReportBase):
    pass


class AdminReportUpdate(BaseModel):
    status: Optional[str] = Field(None, max_length=50)
    data: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = Field(None, max_length=500)
    error_message: Optional[str] = None


class AdminReportOut(AdminReportBase):
    id: int
    generated_by: int
    data: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Dashboard Overview Schemas
class DashboardOverview(BaseModel):
    total_users: int
    total_sellers: int
    total_products: int
    total_orders: int
    total_revenue: float
    pending_approvals: int
    open_support_tickets: int
    system_health: str  # good, warning, critical


class UserManagementStats(BaseModel):
    total_users: int
    active_users: int
    suspended_users: int
    pending_kyc: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int


class FinancialStats(BaseModel):
    total_revenue: float
    total_transactions: int
    pending_payments: int
    failed_payments: int
    refunds_processed: int
    revenue_today: float
    revenue_this_week: float
    revenue_this_month: float


class ContentModerationStats(BaseModel):
    pending_reviews: int
    pending_products: int
    pending_ads: int
    reported_content: int
    resolved_today: int
    resolved_this_week: int


class SystemHealthStats(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_connections: int
    response_time_avg: float
    error_rate: float
    uptime: str


# Response Schemas
class AdminUserListResponse(BaseModel):
    admin_users: List[AdminUserOut]
    total: int
    page: int
    page_size: int


class AdminActionListResponse(BaseModel):
    actions: List[AdminActionOut]
    total: int
    page: int
    page_size: int


class SystemConfigListResponse(BaseModel):
    configs: List[SystemConfigOut]
    total: int
    page: int
    page_size: int


class AuditLogListResponse(BaseModel):
    logs: List[AuditLogOut]
    total: int
    page: int
    page_size: int


class SupportTicketListResponse(BaseModel):
    tickets: List[SupportTicketOut]
    total: int
    page: int
    page_size: int


class ContentModerationListResponse(BaseModel):
    items: List[ContentModerationOut]
    total: int
    page: int
    page_size: int


class AdminNotificationListResponse(BaseModel):
    notifications: List[AdminNotificationOut]
    total: int
    page: int
    page_size: int


class IPBlocklistListResponse(BaseModel):
    blocklist: List[IPBlocklistOut]
    total: int
    page: int
    page_size: int


class AdminReportListResponse(BaseModel):
    reports: List[AdminReportOut]
    total: int
    page: int
    page_size: int


# Permission Management
class PermissionCheck(BaseModel):
    permission: AdminPermission
    has_permission: bool
    message: Optional[str] = None


class RolePermissions(BaseModel):
    role: AdminRole
    permissions: List[AdminPermission]
    description: str


# Bulk Operations
class BulkUserAction(BaseModel):
    user_ids: List[int]
    action: str  # suspend, activate, delete, verify_kyc
    reason: Optional[str] = None


class BulkContentAction(BaseModel):
    content_ids: List[int]
    content_type: str  # product, review, ad
    action: str  # approve, reject, delete
    reason: Optional[str] = None


# Search and Filter Schemas
class AdminSearchFilters(BaseModel):
    search: Optional[str] = None
    role: Optional[AdminRole] = None
    status: Optional[str] = None
    category: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    admin_user_id: Optional[int] = None


class AuditLogFilters(BaseModel):
    event_type: Optional[str] = None
    event_category: Optional[str] = None
    user_id: Optional[int] = None
    admin_user_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    target_type: Optional[str] = None


# Export Schemas
class ExportRequest(BaseModel):
    data_type: str  # users, orders, payments, analytics
    format: str  # csv, json, excel
    filters: Optional[Dict[str, Any]] = None
    include_columns: Optional[List[str]] = None
    exclude_columns: Optional[List[str]] = None


class ExportResponse(BaseModel):
    export_id: str
    status: str  # processing, completed, failed
    file_url: Optional[str] = None
    estimated_completion: Optional[datetime] = None
    error_message: Optional[str] = None
