"""
Admin Dashboard System Models
Comprehensive administrative capabilities for the B2B marketplace
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.db.base import Base


class AdminActionType(str, enum.Enum):
    USER_MANAGEMENT = "user_management"
    CONTENT_MODERATION = "content_moderation"
    PAYMENT_MANAGEMENT = "payment_management"
    AD_APPROVAL = "ad_approval"
    SYSTEM_CONFIG = "system_config"
    SECURITY = "security"
    ANALYTICS = "analytics"
    SUPPORT = "support"


class AdminActionStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"


class AdminRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    SUPPORT = "support"
    ANALYST = "analyst"


class AdminPermission(str, enum.Enum):
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


class AdminUser(Base):
    """Admin user model"""
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    role = Column(Enum(AdminRole), nullable=False, default=AdminRole.ADMIN)
    permissions = Column(JSON, nullable=True)  # List of AdminPermission values
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    actions = relationship("AdminAction", back_populates="admin_user")


class AdminAction(Base):
    """Admin action log"""
    __tablename__ = "admin_actions"

    id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    action_type = Column(Enum(AdminActionType), nullable=False)
    action_status = Column(Enum(AdminActionStatus), default=AdminActionStatus.PENDING)
    
    # Action details
    target_type = Column(String(100), nullable=True)  # user, product, payment, etc.
    target_id = Column(Integer, nullable=True)
    description = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)  # Additional action details
    
    # Metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    admin_user = relationship("AdminUser", back_populates="actions")


class SystemConfig(Base):
    """System configuration settings"""
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), nullable=False, unique=True)
    value = Column(Text, nullable=True)
    value_type = Column(String(50), nullable=False)  # string, integer, float, boolean, json
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # general, security, payment, etc.
    is_public = Column(Boolean, default=False)  # Whether this config is visible to non-admins
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AuditLog(Base):
    """System audit log"""
    __tablename__ = "audit_logs"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    admin_user_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    
    # Event details
    event_type = Column(String(100), nullable=False)
    event_category = Column(String(100), nullable=True)
    description = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    
    # Target information
    target_type = Column(String(100), nullable=True)
    target_id = Column(Integer, nullable=True)
    
    # Security information
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(255), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    admin_user = relationship("AdminUser")


class SupportTicket(Base):
    """Support ticket system"""
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_admin_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    
    # Ticket details
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)  # technical, billing, general, etc.
    priority = Column(String(50), nullable=False)  # low, medium, high, urgent
    status = Column(String(50), nullable=False)  # open, in_progress, resolved, closed
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User")
    assigned_admin = relationship("AdminUser")
    messages = relationship("SupportMessage", back_populates="ticket")


class SupportMessage(Base):
    """Support ticket messages"""
    __tablename__ = "support_messages"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("support_tickets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    admin_user_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    
    # Message details
    content = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # Internal admin notes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ticket = relationship("SupportTicket", back_populates="messages")
    user = relationship("User")
    admin_user = relationship("AdminUser")


class ContentModeration(Base):
    """Content moderation queue"""
    __tablename__ = "content_moderation"

    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String(100), nullable=False)  # product, review, message, ad
    content_id = Column(Integer, nullable=False)
    reported_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_admin_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    
    # Moderation details
    reason = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False)  # pending, reviewed, approved, rejected
    action_taken = Column(String(100), nullable=True)  # warning, suspension, deletion, etc.
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    reported_user = relationship("User", foreign_keys=[reported_by])
    assigned_admin = relationship("AdminUser")


class SystemMetrics(Base):
    """System performance metrics"""
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(255), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50), nullable=True)
    category = Column(String(100), nullable=True)  # performance, security, business, etc.
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    extra_metadata = Column("metadata", JSON, nullable=True)  # Additional metric data


class AdminDashboard(Base):
    """Admin dashboard configuration"""
    __tablename__ = "admin_dashboards"

    id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Dashboard configuration
    layout = Column(JSON, nullable=True)  # Dashboard layout configuration
    widgets = Column(JSON, nullable=True)  # Widget configuration
    filters = Column(JSON, nullable=True)  # Default filters
    
    # Settings
    is_default = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)  # Shareable with other admins
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    admin_user = relationship("AdminUser")


class AdminNotification(Base):
    """Admin notifications"""
    __tablename__ = "admin_notifications"

    id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    
    # Notification details
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(100), nullable=False)  # alert, warning, info, success
    category = Column(String(100), nullable=True)  # system, security, user, etc.
    
    # Action details
    action_url = Column(String(500), nullable=True)
    action_text = Column(String(100), nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False)
    is_urgent = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    admin_user = relationship("AdminUser")


class IPBlocklist(Base):
    """IP address blocklist"""
    __tablename__ = "ip_blocklist"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), nullable=False, unique=True)
    reason = Column(Text, nullable=False)
    block_type = Column(String(50), nullable=False)  # permanent, temporary, rate_limit
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    added_by = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    admin_user = relationship("AdminUser")


class AdminReport(Base):
    """Admin reports and analytics"""
    __tablename__ = "admin_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_name = Column(String(255), nullable=False)
    report_type = Column(String(100), nullable=False)  # daily, weekly, monthly, custom
    generated_by = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    
    # Report details
    parameters = Column(JSON, nullable=True)  # Report parameters
    data = Column(JSON, nullable=True)  # Report data
    file_path = Column(String(500), nullable=True)  # Path to exported file
    
    # Status
    status = Column(String(50), nullable=False)  # generating, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    admin_user = relationship("AdminUser")


