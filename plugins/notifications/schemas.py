"""
Notification System Schemas
Comprehensive notification capabilities for the B2B marketplace
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
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


class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationChannel(str, Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"


class NotificationPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


# Notification Schemas
class NotificationBase(BaseModel):
    type: NotificationType
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    summary: Optional[str] = Field(None, max_length=500)
    data: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None
    action_url: Optional[str] = None
    priority: NotificationPriority = NotificationPriority.NORMAL
    channels: Optional[List[NotificationChannel]] = None
    scheduled_at: Optional[datetime] = None
    source_type: Optional[str] = None
    source_id: Optional[int] = None


class NotificationCreate(NotificationBase):
    user_id: int


class NotificationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    message: Optional[str] = Field(None, min_length=1)
    summary: Optional[str] = Field(None, max_length=500)
    data: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None
    action_url: Optional[str] = None
    priority: Optional[NotificationPriority] = None
    channels: Optional[List[NotificationChannel]] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[NotificationStatus] = None


class NotificationOut(NotificationBase):
    id: int
    user_id: int
    status: NotificationStatus
    sent_channels: Optional[List[str]] = None
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes = True


# Notification Delivery Attempt Schemas
)
class NotificationDeliveryAttemptBase(BaseModel):
    channel: NotificationChannel
    status: str
    error_message: Optional[str] = None
    retry_count: int = 0
    next_retry_at: Optional[datetime] = None
    external_id: Optional[str] = None


class NotificationDeliveryAttemptCreate(NotificationDeliveryAttemptBase):
    notification_id: int


class NotificationDeliveryAttemptUpdate(BaseModel):
    status: Optional[str] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: Optional[int] = None
    next_retry_at: Optional[datetime] = None
    external_id: Optional[str] = None


class NotificationDeliveryAttemptOut(NotificationDeliveryAttemptBase):
    id: int
    notification_id: int
    sent_at: datetime
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes = True


# Notification Template Schemas
)
class NotificationTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: NotificationType
    language: str = "en"
    title_template: str = Field(..., min_length=1, max_length=255)
    message_template: str = Field(..., min_length=1)
    summary_template: Optional[str] = Field(None, max_length=500)
    email_subject: Optional[str] = Field(None, max_length=255)
    email_body: Optional[str] = None
    sms_template: Optional[str] = Field(None, max_length=160)
    push_title: Optional[str] = Field(None, max_length=100)
    push_body: Optional[str] = Field(None, max_length=200)
    channels: Optional[List[NotificationChannel]] = None
    priority: NotificationPriority = NotificationPriority.NORMAL
    is_active: bool = True
    variables: Optional[List[str]] = None


class NotificationTemplateCreate(NotificationTemplateBase):
    pass


class NotificationTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    language: Optional[str] = None
    title_template: Optional[str] = Field(None, min_length=1, max_length=255)
    message_template: Optional[str] = Field(None, min_length=1)
    summary_template: Optional[str] = Field(None, max_length=500)
    email_subject: Optional[str] = Field(None, max_length=255)
    email_body: Optional[str] = None
    sms_template: Optional[str] = Field(None, max_length=160)
    push_title: Optional[str] = Field(None, max_length=100)
    push_body: Optional[str] = Field(None, max_length=200)
    channels: Optional[List[NotificationChannel]] = None
    priority: Optional[NotificationPriority] = None
    is_active: Optional[bool] = None
    variables: Optional[List[str]] = None


class NotificationTemplateOut(NotificationTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes = True


# User Notification Preference Schemas
)
class UserNotificationPreferenceBase(BaseModel):
    notification_type: NotificationType
    in_app_enabled: bool = True
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = True
    quiet_hours_start: Optional[str] = None  # HH:MM format
    quiet_hours_end: Optional[str] = None  # HH:MM format
    timezone: Optional[str] = None
    frequency: str = "immediate"  # immediate, daily, weekly, never
    
    @field_validator('quiet_hours_start', 'quiet_hours_end')
    def validate_time_format(cls, v):
        if v is not None:
            try:
                hour, minute = map(int, v.split(':'))
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    raise ValueError
            except ValueError:
                raise ValueError('Time must be in HH:MM format')
        return v


class UserNotificationPreferenceCreate(UserNotificationPreferenceBase):
    user_id: int


class UserNotificationPreferenceUpdate(BaseModel):
    in_app_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    timezone: Optional[str] = None
    frequency: Optional[str] = None


class UserNotificationPreferenceOut(UserNotificationPreferenceBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes = True


# Notification Subscription Schemas
)
class NotificationSubscriptionBase(BaseModel):
    topic: str = Field(..., min_length=1, max_length=100)
    entity_type: Optional[str] = Field(None, max_length=50)
    entity_id: Optional[int] = None
    is_active: bool = True
    channels: Optional[List[NotificationChannel]] = None


class NotificationSubscriptionCreate(NotificationSubscriptionBase):
    user_id: int


class NotificationSubscriptionUpdate(BaseModel):
    is_active: Optional[bool] = None
    channels: Optional[List[NotificationChannel]] = None


class NotificationSubscriptionOut(NotificationSubscriptionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes = True


# Notification Batch Schemas
)
class NotificationBatchBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    template_id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    target_type: str = Field(..., min_length=1)  # all_users, specific_users, user_segment
    target_data: Optional[Dict[str, Any]] = None
    channels: Optional[List[NotificationChannel]] = None
    scheduled_at: Optional[datetime] = None


class NotificationBatchCreate(NotificationBatchBase):
    pass


class NotificationBatchUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    message: Optional[str] = Field(None, min_length=1)
    target_data: Optional[Dict[str, Any]] = None
    channels: Optional[List[NotificationChannel]] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[str] = None


class NotificationBatchOut(NotificationBatchBase):
    id: int
    status: str
    total_recipients: int
    sent_count: int
    failed_count: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes = True


# Notification Webhook Schemas
)
class NotificationWebhookBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    url: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    notification_types: Optional[List[NotificationType]] = None
    headers: Optional[Dict[str, str]] = None
    secret_key: Optional[str] = None
    is_active: bool = True


class NotificationWebhookCreate(NotificationWebhookBase):
    pass


class NotificationWebhookUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    url: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    notification_types: Optional[List[NotificationType]] = None
    headers: Optional[Dict[str, str]] = None
    secret_key: Optional[str] = None
    is_active: Optional[bool] = None


class NotificationWebhookOut(NotificationWebhookBase):
    id: int
    last_triggered_at: Optional[datetime] = None
    success_count: int
    failure_count: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes = True


# Notification Analytics Schemas
)
class NotificationAnalyticsBase(BaseModel):
    date: datetime
    total_sent: int = 0
    total_delivered: int = 0
    total_read: int = 0
    total_failed: int = 0
    in_app_sent: int = 0
    email_sent: int = 0
    sms_sent: int = 0
    push_sent: int = 0
    notifications_by_type: Optional[Dict[str, int]] = None
    avg_delivery_time_ms: int = 0
    avg_read_time_ms: int = 0


class NotificationAnalyticsCreate(NotificationAnalyticsBase):
    pass


class NotificationAnalyticsOut(NotificationAnalyticsBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes = True


# Request/Response Schemas
)
class NotificationListResponse(BaseModel):
    notifications: List[NotificationOut]
    total: int
    page: int
    page_size: int
    unread_count: int


class NotificationPreferenceListResponse(BaseModel):
    preferences: List[UserNotificationPreferenceOut]
    total: int


class NotificationSubscriptionListResponse(BaseModel):
    subscriptions: List[NotificationSubscriptionOut]
    total: int


class NotificationTemplateListResponse(BaseModel):
    templates: List[NotificationTemplateOut]
    total: int
    page: int
    page_size: int


class NotificationBatchListResponse(BaseModel):
    batches: List[NotificationBatchOut]
    total: int
    page: int
    page_size: int


class NotificationWebhookListResponse(BaseModel):
    webhooks: List[NotificationWebhookOut]
    total: int
    page: int
    page_size: int


class NotificationAnalyticsListResponse(BaseModel):
    analytics: List[NotificationAnalyticsOut]
    total: int
    page: int
    page_size: int


# Advanced Notification Schemas
class BulkNotificationRequest(BaseModel):
    user_ids: List[int]
    notification_data: NotificationBase
    channels: Optional[List[NotificationChannel]] = None
    scheduled_at: Optional[datetime] = None


class NotificationTemplateRenderRequest(BaseModel):
    template_id: int
    variables: Dict[str, Any]
    language: Optional[str] = "en"


class NotificationTemplateRenderResponse(BaseModel):
    title: str
    message: str
    summary: Optional[str] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    sms_template: Optional[str] = None
    push_title: Optional[str] = None
    push_body: Optional[str] = None


class NotificationSendRequest(BaseModel):
    user_id: int
    type: NotificationType
    title: str
    message: str
    summary: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None
    action_url: Optional[str] = None
    priority: NotificationPriority = NotificationPriority.NORMAL
    channels: Optional[List[NotificationChannel]] = None
    scheduled_at: Optional[datetime] = None
    source_type: Optional[str] = None
    source_id: Optional[int] = None


class NotificationSendResponse(BaseModel):
    notification_id: int
    status: NotificationStatus
    delivery_attempts: List[NotificationDeliveryAttemptOut]


class NotificationMarkReadRequest(BaseModel):
    notification_ids: List[int]


class NotificationMarkReadResponse(BaseModel):
    marked_count: int
    notifications: List[NotificationOut]


class NotificationPreferencesUpdateRequest(BaseModel):
    preferences: List[UserNotificationPreferenceUpdate]


class NotificationPreferencesUpdateResponse(BaseModel):
    updated_count: int
    preferences: List[UserNotificationPreferenceOut]


# Analytics and Reporting Schemas
class NotificationAnalyticsSummary(BaseModel):
    total_notifications: int
    total_sent: int
    total_delivered: int
    total_read: int
    total_failed: int
    delivery_rate: float
    read_rate: float
    avg_delivery_time_ms: float
    avg_read_time_ms: float
    notifications_by_type: Dict[str, int]
    notifications_by_channel: Dict[str, int]
    date_range: Dict[str, datetime]


class NotificationPerformanceMetrics(BaseModel):
    avg_response_time_ms: float
    notifications_per_second: float
    queue_size: int
    active_workers: int
    last_processed_at: datetime


class NotificationTrends(BaseModel):
    date: datetime
    sent_count: int
    delivered_count: int
    read_count: int
    failed_count: int
    delivery_rate: float
    read_rate: float


# WebSocket Schemas
class WebSocketNotificationMessage(BaseModel):
    type: str = "notification"
    notification: NotificationOut


class WebSocketNotificationReadMessage(BaseModel):
    type: str = "notification_read"
    notification_ids: List[int]


class WebSocketNotificationPreferenceMessage(BaseModel):
    type: str = "notification_preference"
    preference: UserNotificationPreferenceOut


# Email and SMS Schemas
class EmailNotificationRequest(BaseModel):
    to_email: str
    subject: str
    body: str
    html_body: Optional[str] = None
    from_email: Optional[str] = None
    reply_to: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None


class SMSNotificationRequest(BaseModel):
    to_phone: str
    message: str
    from_phone: Optional[str] = None


class PushNotificationRequest(BaseModel):
    user_id: int
    title: str
    body: str
    data: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None
    action_url: Optional[str] = None
    priority: NotificationPriority = NotificationPriority.NORMAL


# Notification Queue Schemas
class NotificationQueueItem(BaseModel):
    notification_id: int
    user_id: int
    channel: NotificationChannel
    priority: NotificationPriority
    scheduled_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3


class NotificationQueueStatus(BaseModel):
    queue_size: int
    processing_count: int
    failed_count: int
    avg_processing_time_ms: float
    workers_active: int
    workers_total: int