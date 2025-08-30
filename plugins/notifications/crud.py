"""
Notification System CRUD Operations
Comprehensive notification capabilities for the B2B marketplace
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc, text, case
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import json
import re

from .models import (
    Notification, NotificationDeliveryAttempt, NotificationTemplate, 
    UserNotificationPreference, NotificationSubscription, NotificationBatch,
    NotificationWebhook, NotificationAnalytics, NotificationType, 
    NotificationStatus, NotificationChannel, NotificationPriority
)
from .schemas import (
    NotificationCreate, NotificationUpdate, NotificationOut,
    NotificationDeliveryAttemptCreate, NotificationDeliveryAttemptUpdate, NotificationDeliveryAttemptOut,
    NotificationTemplateCreate, NotificationTemplateUpdate, NotificationTemplateOut,
    UserNotificationPreferenceCreate, UserNotificationPreferenceUpdate, UserNotificationPreferenceOut,
    NotificationSubscriptionCreate, NotificationSubscriptionUpdate, NotificationSubscriptionOut,
    NotificationBatchCreate, NotificationBatchUpdate, NotificationBatchOut,
    NotificationWebhookCreate, NotificationWebhookUpdate, NotificationWebhookOut,
    NotificationAnalyticsCreate, NotificationAnalyticsOut,
    NotificationSendRequest, NotificationSendResponse, NotificationMarkReadRequest,
    NotificationMarkReadResponse, BulkNotificationRequest, NotificationTemplateRenderRequest,
    NotificationTemplateRenderResponse, NotificationAnalyticsSummary, NotificationPerformanceMetrics,
    NotificationTrends
)


# Core Notification CRUD Operations
def create_notification(db: Session, notification_data: NotificationCreate) -> NotificationOut:
    """Create a new notification"""
    db_notification = Notification(**notification_data.dict())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return NotificationOut.from_orm(db_notification)


def get_notification(db: Session, notification_id: int) -> Optional[NotificationOut]:
    """Get notification by ID"""
    db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
    return NotificationOut.from_orm(db_notification) if db_notification else None


def get_user_notifications(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    status: Optional[NotificationStatus] = None,
    notification_type: Optional[NotificationType] = None,
    unread_only: bool = False
) -> Tuple[List[NotificationOut], int, int]:
    """Get user notifications with pagination"""
    query = db.query(Notification).filter(Notification.user_id == user_id)
    
    if status:
        query = query.filter(Notification.status == status.value)
    if notification_type:
        query = query.filter(Notification.type == notification_type.value)
    if unread_only:
        query = query.filter(Notification.read_at.is_(None))
    
    total = query.count()
    unread_count = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.read_at.is_(None)
    ).count()
    
    notifications = query.order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()
    
    return [NotificationOut.from_orm(notification) for notification in notifications], total, unread_count


def update_notification(db: Session, notification_id: int, notification_data: NotificationUpdate) -> Optional[NotificationOut]:
    """Update notification"""
    db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not db_notification:
        return None
    
    for field, value in notification_data.dict(exclude_unset=True).items():
        setattr(db_notification, field, value)
    
    db.commit()
    db.refresh(db_notification)
    return NotificationOut.from_orm(db_notification)


def delete_notification(db: Session, notification_id: int) -> bool:
    """Delete notification"""
    db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not db_notification:
        return False
    
    db.delete(db_notification)
    db.commit()
    return True


def mark_notification_read(db: Session, notification_id: int, user_id: int) -> Optional[NotificationOut]:
    """Mark notification as read"""
    db_notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()
    
    if not db_notification:
        return None
    
    db_notification.read_at = datetime.utcnow()
    db_notification.status = NotificationStatus.READ.value
    db.commit()
    db.refresh(db_notification)
    
    return NotificationOut.from_orm(db_notification)


def mark_notifications_read(db: Session, notification_ids: List[int], user_id: int) -> NotificationMarkReadResponse:
    """Mark multiple notifications as read"""
    notifications = db.query(Notification).filter(
        Notification.id.in_(notification_ids),
        Notification.user_id == user_id
    ).all()
    
    marked_count = 0
    for notification in notifications:
        if notification.read_at is None:
            notification.read_at = datetime.utcnow()
            notification.status = NotificationStatus.READ.value
            marked_count += 1
    
    db.commit()
    
    return NotificationMarkReadResponse(
        marked_count=marked_count,
        notifications=[NotificationOut.from_orm(n) for n in notifications]
    )


def mark_all_notifications_read(db: Session, user_id: int) -> int:
    """Mark all user notifications as read"""
    result = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.read_at.is_(None)
    ).update({
        Notification.read_at: datetime.utcnow(),
        Notification.status: NotificationStatus.READ.value
    })
    
    db.commit()
    return result


# Notification Sending and Delivery
def send_notification(db: Session, send_request: NotificationSendRequest) -> NotificationSendResponse:
    """Send a notification to a user"""
    # Create notification
    notification_data = NotificationCreate(
        user_id=send_request.user_id,
        type=send_request.type,
        title=send_request.title,
        message=send_request.message,
        summary=send_request.summary,
        data=send_request.data,
        image_url=send_request.image_url,
        action_url=send_request.action_url,
        priority=send_request.priority,
        channels=send_request.channels,
        scheduled_at=send_request.scheduled_at,
        source_type=send_request.source_type,
        source_id=send_request.source_id
    )
    
    notification = create_notification(db, notification_data)
    
    # Get user preferences
    preferences = get_user_notification_preferences(db, send_request.user_id)
    
    # Determine channels to send to
    channels_to_send = send_request.channels or [NotificationChannel.IN_APP]
    
    # Filter based on user preferences
    filtered_channels = []
    for channel in channels_to_send:
        if channel == NotificationChannel.IN_APP:
            filtered_channels.append(channel)
        elif channel == NotificationChannel.EMAIL and any(p.email_enabled for p in preferences):
            filtered_channels.append(channel)
        elif channel == NotificationChannel.SMS and any(p.sms_enabled for p in preferences):
            filtered_channels.append(channel)
        elif channel == NotificationChannel.PUSH and any(p.push_enabled for p in preferences):
            filtered_channels.append(channel)
    
    # Create delivery attempts
    delivery_attempts = []
    for channel in filtered_channels:
        attempt_data = NotificationDeliveryAttemptCreate(
            notification_id=notification.id,
            channel=channel,
            status="pending"
        )
        attempt = create_delivery_attempt(db, attempt_data)
        delivery_attempts.append(attempt)
    
    # Update notification with sent channels
    update_data = NotificationUpdate(
        sent_channels=[channel.value for channel in filtered_channels],
        status=NotificationStatus.SENT if not send_request.scheduled_at else NotificationStatus.PENDING
    )
    if not send_request.scheduled_at:
        update_data.sent_at = datetime.utcnow()
    
    updated_notification = update_notification(db, notification.id, update_data)
    
    return NotificationSendResponse(
        notification_id=notification.id,
        status=updated_notification.status,
        delivery_attempts=delivery_attempts
    )


def send_bulk_notifications(db: Session, bulk_request: BulkNotificationRequest) -> List[NotificationSendResponse]:
    """Send notifications to multiple users"""
    responses = []
    
    for user_id in bulk_request.user_ids:
        send_request = NotificationSendRequest(
            user_id=user_id,
            type=bulk_request.notification_data.type,
            title=bulk_request.notification_data.title,
            message=bulk_request.notification_data.message,
            summary=bulk_request.notification_data.summary,
            data=bulk_request.notification_data.data,
            image_url=bulk_request.notification_data.image_url,
            action_url=bulk_request.notification_data.action_url,
            priority=bulk_request.notification_data.priority,
            channels=bulk_request.channels or bulk_request.notification_data.channels,
            scheduled_at=bulk_request.scheduled_at or bulk_request.notification_data.scheduled_at,
            source_type=bulk_request.notification_data.source_type,
            source_id=bulk_request.notification_data.source_id
        )
        
        response = send_notification(db, send_request)
        responses.append(response)
    
    return responses


# Notification Delivery Attempt CRUD Operations
def create_delivery_attempt(db: Session, attempt_data: NotificationDeliveryAttemptCreate) -> NotificationDeliveryAttemptOut:
    """Create a new delivery attempt"""
    db_attempt = NotificationDeliveryAttempt(**attempt_data.dict())
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    return NotificationDeliveryAttemptOut.from_orm(db_attempt)


def get_delivery_attempt(db: Session, attempt_id: int) -> Optional[NotificationDeliveryAttemptOut]:
    """Get delivery attempt by ID"""
    db_attempt = db.query(NotificationDeliveryAttempt).filter(NotificationDeliveryAttempt.id == attempt_id).first()
    return NotificationDeliveryAttemptOut.from_orm(db_attempt) if db_attempt else None


def update_delivery_attempt(db: Session, attempt_id: int, attempt_data: NotificationDeliveryAttemptUpdate) -> Optional[NotificationDeliveryAttemptOut]:
    """Update delivery attempt"""
    db_attempt = db.query(NotificationDeliveryAttempt).filter(NotificationDeliveryAttempt.id == attempt_id).first()
    if not db_attempt:
        return None
    
    for field, value in attempt_data.dict(exclude_unset=True).items():
        setattr(db_attempt, field, value)
    
    db.commit()
    db.refresh(db_attempt)
    return NotificationDeliveryAttemptOut.from_orm(db_attempt)


def get_notification_delivery_attempts(db: Session, notification_id: int) -> List[NotificationDeliveryAttemptOut]:
    """Get all delivery attempts for a notification"""
    attempts = db.query(NotificationDeliveryAttempt).filter(
        NotificationDeliveryAttempt.notification_id == notification_id
    ).all()
    
    return [NotificationDeliveryAttemptOut.from_orm(attempt) for attempt in attempts]


# Notification Template CRUD Operations
def create_notification_template(db: Session, template_data: NotificationTemplateCreate) -> NotificationTemplateOut:
    """Create a new notification template"""
    db_template = NotificationTemplate(**template_data.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return NotificationTemplateOut.from_orm(db_template)


def get_notification_template(db: Session, template_id: int) -> Optional[NotificationTemplateOut]:
    """Get notification template by ID"""
    db_template = db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()
    return NotificationTemplateOut.from_orm(db_template) if db_template else None


def get_notification_templates(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    notification_type: Optional[NotificationType] = None,
    language: Optional[str] = None,
    is_active: Optional[bool] = None
) -> Tuple[List[NotificationTemplateOut], int]:
    """Get notification templates with pagination"""
    query = db.query(NotificationTemplate)
    
    if notification_type:
        query = query.filter(NotificationTemplate.type == notification_type.value)
    if language:
        query = query.filter(NotificationTemplate.language == language)
    if is_active is not None:
        query = query.filter(NotificationTemplate.is_active == is_active)
    
    total = query.count()
    templates = query.offset(skip).limit(limit).all()
    
    return [NotificationTemplateOut.from_orm(template) for template in templates], total


def update_notification_template(db: Session, template_id: int, template_data: NotificationTemplateUpdate) -> Optional[NotificationTemplateOut]:
    """Update notification template"""
    db_template = db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()
    if not db_template:
        return None
    
    for field, value in template_data.dict(exclude_unset=True).items():
        setattr(db_template, field, value)
    
    db.commit()
    db.refresh(db_template)
    return NotificationTemplateOut.from_orm(db_template)


def delete_notification_template(db: Session, template_id: int) -> bool:
    """Delete notification template"""
    db_template = db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()
    if not db_template:
        return False
    
    db.delete(db_template)
    db.commit()
    return True


def render_notification_template(db: Session, render_request: NotificationTemplateRenderRequest) -> NotificationTemplateRenderResponse:
    """Render a notification template with variables"""
    template = get_notification_template(db, render_request.template_id)
    if not template:
        raise ValueError("Template not found")
    
    # Simple template rendering - in production, use a proper templating engine
    variables = render_request.variables or {}
    
    def render_text(text: str) -> str:
        if not text:
            return ""
        for key, value in variables.items():
            text = text.replace(f"{{{{{key}}}}}", str(value))
        return text
    
    return NotificationTemplateRenderResponse(
        title=render_text(template.title_template),
        message=render_text(template.message_template),
        summary=render_text(template.summary_template) if template.summary_template else None,
        email_subject=render_text(template.email_subject) if template.email_subject else None,
        email_body=render_text(template.email_body) if template.email_body else None,
        sms_template=render_text(template.sms_template) if template.sms_template else None,
        push_title=render_text(template.push_title) if template.push_title else None,
        push_body=render_text(template.push_body) if template.push_body else None
    )


# User Notification Preference CRUD Operations
def create_user_notification_preference(db: Session, preference_data: UserNotificationPreferenceCreate) -> UserNotificationPreferenceOut:
    """Create a new user notification preference"""
    db_preference = UserNotificationPreference(**preference_data.dict())
    db.add(db_preference)
    db.commit()
    db.refresh(db_preference)
    return UserNotificationPreferenceOut.from_orm(db_preference)


def get_user_notification_preferences(db: Session, user_id: int) -> List[UserNotificationPreferenceOut]:
    """Get all notification preferences for a user"""
    preferences = db.query(UserNotificationPreference).filter(
        UserNotificationPreference.user_id == user_id
    ).all()
    
    return [UserNotificationPreferenceOut.from_orm(preference) for preference in preferences]


def get_user_notification_preference(
    db: Session, 
    user_id: int, 
    notification_type: NotificationType
) -> Optional[UserNotificationPreferenceOut]:
    """Get specific notification preference for a user"""
    preference = db.query(UserNotificationPreference).filter(
        UserNotificationPreference.user_id == user_id,
        UserNotificationPreference.notification_type == notification_type.value
    ).first()
    
    return UserNotificationPreferenceOut.from_orm(preference) if preference else None


def update_user_notification_preference(
    db: Session, 
    user_id: int, 
    notification_type: NotificationType, 
    preference_data: UserNotificationPreferenceUpdate
) -> Optional[UserNotificationPreferenceOut]:
    """Update user notification preference"""
    preference = db.query(UserNotificationPreference).filter(
        UserNotificationPreference.user_id == user_id,
        UserNotificationPreference.notification_type == notification_type.value
    ).first()
    
    if not preference:
        return None
    
    for field, value in preference_data.dict(exclude_unset=True).items():
        setattr(preference, field, value)
    
    db.commit()
    db.refresh(preference)
    return UserNotificationPreferenceOut.from_orm(preference)


def delete_user_notification_preference(db: Session, user_id: int, notification_type: NotificationType) -> bool:
    """Delete user notification preference"""
    preference = db.query(UserNotificationPreference).filter(
        UserNotificationPreference.user_id == user_id,
        UserNotificationPreference.notification_type == notification_type.value
    ).first()
    
    if not preference:
        return False
    
    db.delete(preference)
    db.commit()
    return True


# Notification Subscription CRUD Operations
def create_notification_subscription(db: Session, subscription_data: NotificationSubscriptionCreate) -> NotificationSubscriptionOut:
    """Create a new notification subscription"""
    db_subscription = NotificationSubscription(**subscription_data.dict())
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return NotificationSubscriptionOut.from_orm(db_subscription)


def get_user_notification_subscriptions(db: Session, user_id: int) -> List[NotificationSubscriptionOut]:
    """Get all notification subscriptions for a user"""
    subscriptions = db.query(NotificationSubscription).filter(
        NotificationSubscription.user_id == user_id,
        NotificationSubscription.is_active == True
    ).all()
    
    return [NotificationSubscriptionOut.from_orm(subscription) for subscription in subscriptions]


def update_notification_subscription(
    db: Session, 
    subscription_id: int, 
    subscription_data: NotificationSubscriptionUpdate
) -> Optional[NotificationSubscriptionOut]:
    """Update notification subscription"""
    subscription = db.query(NotificationSubscription).filter(NotificationSubscription.id == subscription_id).first()
    if not subscription:
        return None
    
    for field, value in subscription_data.dict(exclude_unset=True).items():
        setattr(subscription, field, value)
    
    db.commit()
    db.refresh(subscription)
    return NotificationSubscriptionOut.from_orm(subscription)


def delete_notification_subscription(db: Session, subscription_id: int) -> bool:
    """Delete notification subscription"""
    subscription = db.query(NotificationSubscription).filter(NotificationSubscription.id == subscription_id).first()
    if not subscription:
        return False
    
    db.delete(subscription)
    db.commit()
    return True


# Notification Batch CRUD Operations
def create_notification_batch(db: Session, batch_data: NotificationBatchCreate) -> NotificationBatchOut:
    """Create a new notification batch"""
    db_batch = NotificationBatch(**batch_data.dict())
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return NotificationBatchOut.from_orm(db_batch)


def get_notification_batch(db: Session, batch_id: int) -> Optional[NotificationBatchOut]:
    """Get notification batch by ID"""
    db_batch = db.query(NotificationBatch).filter(NotificationBatch.id == batch_id).first()
    return NotificationBatchOut.from_orm(db_batch) if db_batch else None


def get_notification_batches(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None
) -> Tuple[List[NotificationBatchOut], int]:
    """Get notification batches with pagination"""
    query = db.query(NotificationBatch)
    
    if status:
        query = query.filter(NotificationBatch.status == status)
    
    total = query.count()
    batches = query.order_by(desc(NotificationBatch.created_at)).offset(skip).limit(limit).all()
    
    return [NotificationBatchOut.from_orm(batch) for batch in batches], total


def update_notification_batch(db: Session, batch_id: int, batch_data: NotificationBatchUpdate) -> Optional[NotificationBatchOut]:
    """Update notification batch"""
    db_batch = db.query(NotificationBatch).filter(NotificationBatch.id == batch_id).first()
    if not db_batch:
        return None
    
    for field, value in batch_data.dict(exclude_unset=True).items():
        setattr(db_batch, field, value)
    
    db.commit()
    db.refresh(db_batch)
    return NotificationBatchOut.from_orm(db_batch)


def process_notification_batch(db: Session, batch_id: int) -> bool:
    """Process a notification batch"""
    batch = get_notification_batch(db, batch_id)
    if not batch or batch.status != "pending":
        return False
    
    # Update batch status
    update_data = NotificationBatchUpdate(status="processing", started_at=datetime.utcnow())
    update_notification_batch(db, batch_id, update_data)
    
    # Get target users
    user_ids = []
    if batch.target_type == "all_users":
        # Get all active users
        from app.core.auth.models import User
        users = db.query(User.id).filter(User.is_active == True).all()
        user_ids = [user.id for user in users]
    elif batch.target_type == "specific_users":
        user_ids = batch.target_data.get("user_ids", [])
    elif batch.target_type == "user_segment":
        # Implement user segmentation logic
        pass
    
    # Send notifications
    sent_count = 0
    failed_count = 0
    
    for user_id in user_ids:
        try:
            send_request = NotificationSendRequest(
                user_id=user_id,
                type=NotificationType.NEWSLETTER,  # Default type for batches
                title=batch.title,
                message=batch.message,
                channels=batch.channels,
                scheduled_at=batch.scheduled_at
            )
            send_notification(db, send_request)
            sent_count += 1
        except Exception:
            failed_count += 1
    
    # Update batch with results
    final_update = NotificationBatchUpdate(
        status="completed",
        sent_count=sent_count,
        failed_count=failed_count,
        completed_at=datetime.utcnow()
    )
    update_notification_batch(db, batch_id, final_update)
    
    return True


# Notification Webhook CRUD Operations
def create_notification_webhook(db: Session, webhook_data: NotificationWebhookCreate) -> NotificationWebhookOut:
    """Create a new notification webhook"""
    db_webhook = NotificationWebhook(**webhook_data.dict())
    db.add(db_webhook)
    db.commit()
    db.refresh(db_webhook)
    return NotificationWebhookOut.from_orm(db_webhook)


def get_notification_webhook(db: Session, webhook_id: int) -> Optional[NotificationWebhookOut]:
    """Get notification webhook by ID"""
    db_webhook = db.query(NotificationWebhook).filter(NotificationWebhook.id == webhook_id).first()
    return NotificationWebhookOut.from_orm(db_webhook) if db_webhook else None


def get_notification_webhooks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> Tuple[List[NotificationWebhookOut], int]:
    """Get notification webhooks with pagination"""
    query = db.query(NotificationWebhook)
    
    if is_active is not None:
        query = query.filter(NotificationWebhook.is_active == is_active)
    
    total = query.count()
    webhooks = query.offset(skip).limit(limit).all()
    
    return [NotificationWebhookOut.from_orm(webhook) for webhook in webhooks], total


def update_notification_webhook(db: Session, webhook_id: int, webhook_data: NotificationWebhookUpdate) -> Optional[NotificationWebhookOut]:
    """Update notification webhook"""
    db_webhook = db.query(NotificationWebhook).filter(NotificationWebhook.id == webhook_id).first()
    if not db_webhook:
        return None
    
    for field, value in webhook_data.dict(exclude_unset=True).items():
        setattr(db_webhook, field, value)
    
    db.commit()
    db.refresh(db_webhook)
    return NotificationWebhookOut.from_orm(db_webhook)


def delete_notification_webhook(db: Session, webhook_id: int) -> bool:
    """Delete notification webhook"""
    db_webhook = db.query(NotificationWebhook).filter(NotificationWebhook.id == webhook_id).first()
    if not db_webhook:
        return False
    
    db.delete(db_webhook)
    db.commit()
    return True


# Notification Analytics CRUD Operations
def create_notification_analytics(db: Session, analytics_data: NotificationAnalyticsCreate) -> NotificationAnalyticsOut:
    """Create a new notification analytics entry"""
    db_analytics = NotificationAnalytics(**analytics_data.dict())
    db.add(db_analytics)
    db.commit()
    db.refresh(db_analytics)
    return NotificationAnalyticsOut.from_orm(db_analytics)


def get_notification_analytics(
    db: Session,
    start_date: datetime,
    end_date: datetime,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[NotificationAnalyticsOut], int]:
    """Get notification analytics"""
    query = db.query(NotificationAnalytics).filter(
        NotificationAnalytics.date >= start_date,
        NotificationAnalytics.date <= end_date
    )
    
    total = query.count()
    analytics = query.order_by(desc(NotificationAnalytics.date)).offset(skip).limit(limit).all()
    
    return [NotificationAnalyticsOut.from_orm(analytics) for analytics in analytics], total


def get_notification_analytics_summary(db: Session, start_date: datetime, end_date: datetime) -> NotificationAnalyticsSummary:
    """Get notification analytics summary"""
    # Calculate analytics from delivery attempts
    delivery_stats = db.query(
        func.count(NotificationDeliveryAttempt.id).label('total_sent'),
        func.sum(case([(NotificationDeliveryAttempt.status == 'delivered', 1)], else_=0)).label('total_delivered'),
        func.sum(case([(NotificationDeliveryAttempt.status == 'read', 1)], else_=0)).label('total_read'),
        func.sum(case([(NotificationDeliveryAttempt.status == 'failed', 1)], else_=0)).label('total_failed')
    ).filter(
        NotificationDeliveryAttempt.sent_at >= start_date,
        NotificationDeliveryAttempt.sent_at <= end_date
    ).first()
    
    # Calculate channel breakdown
    channel_stats = db.query(
        NotificationDeliveryAttempt.channel,
        func.count(NotificationDeliveryAttempt.id).label('count')
    ).filter(
        NotificationDeliveryAttempt.sent_at >= start_date,
        NotificationDeliveryAttempt.sent_at <= end_date
    ).group_by(NotificationDeliveryAttempt.channel).all()
    
    # Calculate type breakdown
    type_stats = db.query(
        Notification.type,
        func.count(Notification.id).label('count')
    ).filter(
        Notification.created_at >= start_date,
        Notification.created_at <= end_date
    ).group_by(Notification.type).all()
    
    total_sent = delivery_stats.total_sent or 0
    total_delivered = delivery_stats.total_delivered or 0
    total_read = delivery_stats.total_read or 0
    total_failed = delivery_stats.total_failed or 0
    
    return NotificationAnalyticsSummary(
        total_notifications=total_sent,
        total_sent=total_sent,
        total_delivered=total_delivered,
        total_read=total_read,
        total_failed=total_failed,
        delivery_rate=total_delivered / total_sent if total_sent > 0 else 0,
        read_rate=total_read / total_sent if total_sent > 0 else 0,
        avg_delivery_time_ms=0,  # Calculate from actual delivery times
        avg_read_time_ms=0,  # Calculate from actual read times
        notifications_by_type=dict(type_stats),
        notifications_by_channel=dict(channel_stats),
        date_range={"start": start_date, "end": end_date}
    )


def get_notification_performance_metrics(db: Session) -> NotificationPerformanceMetrics:
    """Get notification performance metrics"""
    # This would calculate actual performance metrics
    # For now, returning placeholder data
    return NotificationPerformanceMetrics(
        avg_response_time_ms=150.0,
        notifications_per_second=10.5,
        queue_size=0,
        active_workers=2,
        last_processed_at=datetime.utcnow()
    )


def get_notification_trends(db: Session, days: int = 30) -> List[NotificationTrends]:
    """Get notification trends over time"""
    trends = []
    
    for i in range(days):
        date = datetime.utcnow() - timedelta(days=i)
        
        # Get stats for this date
        stats = db.query(
            func.count(NotificationDeliveryAttempt.id).label('sent_count'),
            func.sum(case([(NotificationDeliveryAttempt.status == 'delivered', 1)], else_=0)).label('delivered_count'),
            func.sum(case([(NotificationDeliveryAttempt.status == 'read', 1)], else_=0)).label('read_count'),
            func.sum(case([(NotificationDeliveryAttempt.status == 'failed', 1)], else_=0)).label('failed_count')
        ).filter(
            func.date(NotificationDeliveryAttempt.sent_at) == date.date()
        ).first()
        
        sent_count = stats.sent_count or 0
        delivered_count = stats.delivered_count or 0
        read_count = stats.read_count or 0
        failed_count = stats.failed_count or 0
        
        trends.append(NotificationTrends(
            date=date,
            sent_count=sent_count,
            delivered_count=delivered_count,
            read_count=read_count,
            failed_count=failed_count,
            delivery_rate=delivered_count / sent_count if sent_count > 0 else 0,
            read_rate=read_count / sent_count if sent_count > 0 else 0
        ))
    
    return trends


# Utility Functions
def get_pending_notifications(db: Session, limit: int = 100) -> List[Notification]:
    """Get pending notifications for processing"""
    return db.query(Notification).filter(
        Notification.status == NotificationStatus.PENDING.value,
        or_(
            Notification.scheduled_at.is_(None),
            Notification.scheduled_at <= datetime.utcnow()
        )
    ).limit(limit).all()


def get_failed_delivery_attempts(db: Session, limit: int = 100) -> List[NotificationDeliveryAttempt]:
    """Get failed delivery attempts for retry"""
    return db.query(NotificationDeliveryAttempt).filter(
        NotificationDeliveryAttempt.status == "failed",
        NotificationDeliveryAttempt.retry_count < 3,
        or_(
            NotificationDeliveryAttempt.next_retry_at.is_(None),
            NotificationDeliveryAttempt.next_retry_at <= datetime.utcnow()
        )
    ).limit(limit).all()


def cleanup_old_notifications(db: Session, days: int = 90) -> int:
    """Clean up old notifications"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Delete old notifications
    deleted_count = db.query(Notification).filter(
        Notification.created_at < cutoff_date,
        Notification.status.in_([NotificationStatus.READ.value, NotificationStatus.FAILED.value])
    ).delete()
    
    # Delete old delivery attempts
    db.query(NotificationDeliveryAttempt).filter(
        NotificationDeliveryAttempt.sent_at < cutoff_date,
        NotificationDeliveryAttempt.status.in_(["delivered", "failed", "read"])
    ).delete()
    
    db.commit()
    return deleted_count
