"""
Notification System Models
Comprehensive notification capabilities for the B2B marketplace
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.db.base import Base


class NotificationType(str, enum.Enum):
    # User-related notifications
    USER_WELCOME = "user_welcome"
    EMAIL_VERIFICATION = "email_verification"
    PHONE_VERIFICATION = "phone_verification"
    KYC_APPROVED = "kyc_approved"
    KYC_REJECTED = "kyc_rejected"
    PASSWORD_RESET = "password_reset"
    PROFILE_UPDATED = "profile_updated"
    
    # Marketplace notifications
    NEW_MESSAGE = "new_message"
    MESSAGE_READ = "message_read"
    NEW_RFQ = "new_rfq"
    RFQ_QUOTE_RECEIVED = "rfq_quote_received"
    RFQ_QUOTE_ACCEPTED = "rfq_quote_accepted"
    RFQ_QUOTE_REJECTED = "rfq_quote_rejected"
    NEW_ORDER = "new_order"
    ORDER_STATUS_CHANGED = "order_status_changed"
    ORDER_SHIPPED = "order_shipped"
    ORDER_DELIVERED = "order_delivered"
    ORDER_CANCELLED = "order_cancelled"
    
    # Payment notifications
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_FAILED = "payment_failed"
    WALLET_TOPUP = "wallet_topup"
    WALLET_LOW_BALANCE = "wallet_low_balance"
    REFUND_PROCESSED = "refund_processed"
    
    # Seller notifications
    NEW_PRODUCT_APPROVED = "new_product_approved"
    NEW_PRODUCT_REJECTED = "new_product_rejected"
    STORE_VERIFIED = "store_verified"
    STORE_SUSPENDED = "store_suspended"
    NEW_REVIEW = "new_review"
    REVIEW_RESPONSE = "review_response"
    
    # Advertising notifications
    AD_APPROVED = "ad_approved"
    AD_REJECTED = "ad_rejected"
    AD_PAUSED = "ad_paused"
    AD_BUDGET_LOW = "ad_budget_low"
    AD_CAMPAIGN_ENDED = "ad_campaign_ended"
    
    # System notifications
    SYSTEM_MAINTENANCE = "system_maintenance"
    SYSTEM_UPDATE = "system_update"
    SECURITY_ALERT = "security_alert"
    NEWSLETTER = "newsletter"
    PROMOTIONAL = "promotional"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationChannel(str, enum.Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"


class NotificationPriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Notification(Base):
    """Main notification table"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    
    # Recipient
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Notification details
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    summary = Column(String(500), nullable=True)
    
    # Content and data
    data = Column(JSON, nullable=True)  # Additional data for the notification
    image_url = Column(String(500), nullable=True)
    action_url = Column(String(500), nullable=True)  # URL to navigate to when clicked
    
    # Status and priority
    status = Column(String(20), default=NotificationStatus.PENDING.value)
    priority = Column(String(20), default=NotificationPriority.NORMAL.value)
    
    # Channels
    channels = Column(JSON, nullable=True)  # Array of channels to send to
    sent_channels = Column(JSON, nullable=True)  # Array of channels successfully sent to
    
    # Timing
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    source_type = Column(String(50), nullable=True)  # user, system, admin, etc.
    source_id = Column(Integer, nullable=True)  # ID of the source entity
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    delivery_attempts = relationship("NotificationDeliveryAttempt", back_populates="notification")


class NotificationDeliveryAttempt(Base):
    """Track delivery attempts for each channel"""
    __tablename__ = "notification_delivery_attempts"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"), nullable=False)
    
    # Channel details
    channel = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)
    
    # Delivery details
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    
    # External IDs
    external_id = Column(String(255), nullable=True)  # ID from external service (email, SMS, etc.)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    notification = relationship("Notification", back_populates="delivery_attempts")


class NotificationTemplate(Base):
    """Notification templates for different types"""
    __tablename__ = "notification_templates"

    id = Column(Integer, primary_key=True, index=True)
    
    # Template details
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    language = Column(String(10), default="en")
    
    # Content
    title_template = Column(String(255), nullable=False)
    message_template = Column(Text, nullable=False)
    summary_template = Column(String(500), nullable=True)
    
    # Channel-specific templates
    email_subject = Column(String(255), nullable=True)
    email_body = Column(Text, nullable=True)
    sms_template = Column(String(160), nullable=True)  # SMS character limit
    push_title = Column(String(100), nullable=True)
    push_body = Column(String(200), nullable=True)
    
    # Configuration
    channels = Column(JSON, nullable=True)  # Default channels for this template
    priority = Column(String(20), default=NotificationPriority.NORMAL.value)
    is_active = Column(Boolean, default=True)
    
    # Variables
    variables = Column(JSON, nullable=True)  # Available variables for this template
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class UserNotificationPreference(Base):
    """User preferences for notifications"""
    __tablename__ = "user_notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Notification type preferences
    notification_type = Column(String(50), nullable=False)
    
    # Channel preferences
    in_app_enabled = Column(Boolean, default=True)
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    push_enabled = Column(Boolean, default=True)
    
    # Timing preferences
    quiet_hours_start = Column(String(5), nullable=True)  # HH:MM format
    quiet_hours_end = Column(String(5), nullable=True)  # HH:MM format
    timezone = Column(String(50), nullable=True)
    
    # Frequency preferences
    frequency = Column(String(20), default="immediate")  # immediate, daily, weekly, never
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notification_preferences")


class NotificationSubscription(Base):
    """User subscriptions to notification topics"""
    __tablename__ = "notification_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Subscription details
    topic = Column(String(100), nullable=False)  # e.g., "new_products", "price_alerts"
    entity_type = Column(String(50), nullable=True)  # product, seller, etc.
    entity_id = Column(Integer, nullable=True)  # Specific entity ID
    
    # Subscription settings
    is_active = Column(Boolean, default=True)
    channels = Column(JSON, nullable=True)  # Channels for this subscription
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notification_subscriptions")


class NotificationBatch(Base):
    """Batch notifications for bulk sending"""
    __tablename__ = "notification_batches"

    id = Column(Integer, primary_key=True, index=True)
    
    # Batch details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Template and content
    template_id = Column(Integer, ForeignKey("notification_templates.id"), nullable=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Target audience
    target_type = Column(String(50), nullable=False)  # all_users, specific_users, user_segment
    target_data = Column(JSON, nullable=True)  # User IDs, segment criteria, etc.
    
    # Channels and timing
    channels = Column(JSON, nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    total_recipients = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    
    # Progress tracking
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    template = relationship("NotificationTemplate")


class NotificationWebhook(Base):
    """Webhook configurations for external integrations"""
    __tablename__ = "notification_webhooks"

    id = Column(Integer, primary_key=True, index=True)
    
    # Webhook details
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuration
    notification_types = Column(JSON, nullable=True)  # Types to forward
    headers = Column(JSON, nullable=True)  # Custom headers
    secret_key = Column(String(255), nullable=True)  # For signature verification
    
    # Status
    is_active = Column(Boolean, default=True)
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class NotificationAnalytics(Base):
    """Analytics for notification performance"""
    __tablename__ = "notification_analytics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False)
    
    # Metrics
    total_sent = Column(Integer, default=0)
    total_delivered = Column(Integer, default=0)
    total_read = Column(Integer, default=0)
    total_failed = Column(Integer, default=0)
    
    # Channel breakdown
    in_app_sent = Column(Integer, default=0)
    email_sent = Column(Integer, default=0)
    sms_sent = Column(Integer, default=0)
    push_sent = Column(Integer, default=0)
    
    # Type breakdown
    notifications_by_type = Column(JSON, nullable=True)  # Count by notification type
    
    # Performance metrics
    avg_delivery_time_ms = Column(Integer, default=0)
    avg_read_time_ms = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Create indexes for better performance
Index('idx_notifications_user_status', Notification.user_id, Notification.status)
Index('idx_notifications_type_status', Notification.type, Notification.status)
Index('idx_notifications_scheduled', Notification.scheduled_at)
Index('idx_notifications_created', Notification.created_at.desc())

Index('idx_delivery_attempts_notification', NotificationDeliveryAttempt.notification_id)
Index('idx_delivery_attempts_channel_status', NotificationDeliveryAttempt.channel, NotificationDeliveryAttempt.status)
Index('idx_delivery_attempts_sent', NotificationDeliveryAttempt.sent_at.desc())

Index('idx_templates_type_language', NotificationTemplate.type, NotificationTemplate.language)
Index('idx_templates_active', NotificationTemplate.is_active)

Index('idx_user_preferences_user_type', UserNotificationPreference.user_id, UserNotificationPreference.notification_type)
Index('idx_user_preferences_enabled', UserNotificationPreference.in_app_enabled, UserNotificationPreference.email_enabled)

Index('idx_subscriptions_user_topic', NotificationSubscription.user_id, NotificationSubscription.topic)
Index('idx_subscriptions_active', NotificationSubscription.is_active)

Index('idx_batches_status', NotificationBatch.status)
Index('idx_batches_scheduled', NotificationBatch.scheduled_at)

Index('idx_analytics_date', NotificationAnalytics.date)
