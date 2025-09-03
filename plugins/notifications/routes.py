"""
Notification System Routes
Comprehensive notification capabilities for the B2B marketplace
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import asyncio

from app.core.auth import get_current_user_sync as get_current_user, get_current_user_optional_sync as get_current_user_optional
from plugins.auth.models import User
from . import crud, schemas
from .schemas import NotificationType, NotificationStatus, NotificationChannel, NotificationPriority

router = APIRouter(prefix="/notifications", tags=["notifications"])


# Lazy generator-style DB dependency to avoid circular imports
def db_dep():
    from app.db.session import get_db_sync
    yield from get_db_sync()


# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_notification(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except Exception:
                self.disconnect(user_id)

    async def broadcast(self, message: dict):
        for user_id in list(self.active_connections.keys()):
            await self.send_notification(user_id, message)


manager = ConnectionManager()


# WebSocket endpoint for real-time notifications
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            elif message.get("type") == "mark_read":
                # Mark notifications as read
                notification_ids = message.get("notification_ids", [])
                # This would be handled in a background task
                pass
            
    except WebSocketDisconnect:
        manager.disconnect(user_id)


# Core Notification Routes
@router.get("/", response_model=schemas.NotificationListResponse)
def get_user_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[NotificationStatus] = None,
    notification_type: Optional[NotificationType] = None,
    unread_only: bool = Query(False),
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get user notifications"""
    notifications, total, unread_count = crud.get_user_notifications(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status,
        notification_type=notification_type,
        unread_only=unread_only
    )
    
    return schemas.NotificationListResponse(
        notifications=notifications,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        unread_count=unread_count
    )


@router.get("/{notification_id}", response_model=schemas.NotificationOut)
def get_notification(
    notification_id: int,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get specific notification"""
    notification = crud.get_notification(db, notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return notification


@router.post("/mark-read", response_model=schemas.NotificationMarkReadResponse)
def mark_notifications_read(
    request: schemas.NotificationMarkReadRequest,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Mark notifications as read"""
    return crud.mark_notifications_read(db, request.notification_ids, current_user.id)


@router.post("/mark-read/{notification_id}", response_model=schemas.NotificationOut)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Mark a single notification as read"""
    notification = crud.mark_notification_read(db, notification_id, current_user.id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return notification


@router.post("/mark-all-read")
def mark_all_notifications_read(
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Mark all user notifications as read"""
    count = crud.mark_all_notifications_read(db, current_user.id)
    return {"message": f"Marked {count} notifications as read"}


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Delete a notification"""
    notification = crud.get_notification(db, notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    success = crud.delete_notification(db, notification_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete notification")
    
    return {"message": "Notification deleted successfully"}


# Notification Sending Routes
@router.post("/send", response_model=schemas.NotificationSendResponse)
def send_notification(
    request: schemas.NotificationSendRequest,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Send a notification to a user"""
    # Check if user has permission to send notifications
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return crud.send_notification(db, request)


@router.post("/send-bulk", response_model=List[schemas.NotificationSendResponse])
def send_bulk_notifications(
    request: schemas.BulkNotificationRequest,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Send notifications to multiple users"""
    # Check if user has permission to send bulk notifications
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return crud.send_bulk_notifications(db, request)


# User Notification Preferences Routes
@router.get("/preferences", response_model=schemas.NotificationPreferenceListResponse)
def get_user_notification_preferences(
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get user notification preferences"""
    preferences = crud.get_user_notification_preferences(db, current_user.id)
    return schemas.NotificationPreferenceListResponse(preferences=preferences, total=len(preferences))


@router.get("/preferences/{notification_type}", response_model=schemas.UserNotificationPreferenceOut)
def get_user_notification_preference(
    notification_type: NotificationType,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get specific notification preference"""
    preference = crud.get_user_notification_preference(db, current_user.id, notification_type)
    if not preference:
        raise HTTPException(status_code=404, detail="Preference not found")
    
    return preference


@router.patch("/preferences/{notification_type}", response_model=schemas.UserNotificationPreferenceOut)
def update_user_notification_preference(
    notification_type: NotificationType,
    preference_data: schemas.UserNotificationPreferenceUpdate,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Update user notification preference"""
    preference = crud.update_user_notification_preference(db, current_user.id, notification_type, preference_data)
    if not preference:
        raise HTTPException(status_code=404, detail="Preference not found")
    
    return preference


@router.post("/preferences/{notification_type}", response_model=schemas.UserNotificationPreferenceOut)
def create_user_notification_preference(
    notification_type: NotificationType,
    preference_data: schemas.UserNotificationPreferenceUpdate,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Create user notification preference"""
    # Check if preference already exists
    existing = crud.get_user_notification_preference(db, current_user.id, notification_type)
    if existing:
        raise HTTPException(status_code=400, detail="Preference already exists")
    
    create_data = schemas.UserNotificationPreferenceCreate(
        user_id=current_user.id,
        notification_type=notification_type,
        **preference_data.dict()
    )
    
    return crud.create_user_notification_preference(db, create_data)


@router.delete("/preferences/{notification_type}")
def delete_user_notification_preference(
    notification_type: NotificationType,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Delete user notification preference"""
    success = crud.delete_user_notification_preference(db, current_user.id, notification_type)
    if not success:
        raise HTTPException(status_code=404, detail="Preference not found")
    
    return {"message": "Preference deleted successfully"}


# Notification Subscriptions Routes
@router.get("/subscriptions", response_model=schemas.NotificationSubscriptionListResponse)
def get_user_notification_subscriptions(
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get user notification subscriptions"""
    subscriptions = crud.get_user_notification_subscriptions(db, current_user.id)
    return schemas.NotificationSubscriptionListResponse(subscriptions=subscriptions, total=len(subscriptions))


@router.post("/subscriptions", response_model=schemas.NotificationSubscriptionOut)
def create_notification_subscription(
    subscription_data: schemas.NotificationSubscriptionCreate,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Create notification subscription"""
    subscription_data.user_id = current_user.id
    return crud.create_notification_subscription(db, subscription_data)


@router.patch("/subscriptions/{subscription_id}", response_model=schemas.NotificationSubscriptionOut)
def update_notification_subscription(
    subscription_id: int,
    subscription_data: schemas.NotificationSubscriptionUpdate,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Update notification subscription"""
    subscription = crud.update_notification_subscription(db, subscription_id, subscription_data)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return subscription


@router.delete("/subscriptions/{subscription_id}")
def delete_notification_subscription(
    subscription_id: int,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Delete notification subscription"""
    success = crud.delete_notification_subscription(db, subscription_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return {"message": "Subscription deleted successfully"}


# Notification Templates Routes (Admin only)
@router.post("/templates", response_model=schemas.NotificationTemplateOut)
def create_notification_template(
    template_data: schemas.NotificationTemplateCreate,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Create notification template"""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return crud.create_notification_template(db, template_data)


@router.get("/templates", response_model=schemas.NotificationTemplateListResponse)
def get_notification_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    notification_type: Optional[NotificationType] = None,
    language: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get notification templates"""
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    templates, total = crud.get_notification_templates(
        db=db,
        skip=skip,
        limit=limit,
        notification_type=notification_type,
        language=language,
        is_active=is_active
    )
    
    return schemas.NotificationTemplateListResponse(
        templates=templates,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/templates/{template_id}", response_model=schemas.NotificationTemplateOut)
def get_notification_template(
    template_id: int,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get notification template by ID"""
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    template = crud.get_notification_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return template


@router.patch("/templates/{template_id}", response_model=schemas.NotificationTemplateOut)
def update_notification_template(
    template_id: int,
    template_data: schemas.NotificationTemplateUpdate,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Update notification template"""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    template = crud.update_notification_template(db, template_id, template_data)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return template


@router.delete("/templates/{template_id}")
def delete_notification_template(
    template_id: int,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Delete notification template"""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    success = crud.delete_notification_template(db, template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {"message": "Template deleted successfully"}


@router.post("/templates/{template_id}/render", response_model=schemas.NotificationTemplateRenderResponse)
def render_notification_template(
    template_id: int,
    render_request: schemas.NotificationTemplateRenderRequest,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Render notification template with variables"""
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        return crud.render_notification_template(db, render_request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Notification Batch Routes (Admin only)
@router.post("/batches", response_model=schemas.NotificationBatchOut)
def create_notification_batch(
    batch_data: schemas.NotificationBatchCreate,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Create notification batch"""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return crud.create_notification_batch(db, batch_data)


@router.get("/batches", response_model=schemas.NotificationBatchListResponse)
def get_notification_batches(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get notification batches"""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    batches, total = crud.get_notification_batches(
        db=db,
        skip=skip,
        limit=limit,
        status=status
    )
    
    return schemas.NotificationBatchListResponse(
        batches=batches,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/batches/{batch_id}", response_model=schemas.NotificationBatchOut)
def get_notification_batch(
    batch_id: int,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get notification batch by ID"""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    batch = crud.get_notification_batch(db, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    return batch


@router.patch("/batches/{batch_id}", response_model=schemas.NotificationBatchOut)
def update_notification_batch(
    batch_id: int,
    batch_data: schemas.NotificationBatchUpdate,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Update notification batch"""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    batch = crud.update_notification_batch(db, batch_id, batch_data)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    return batch


@router.post("/batches/{batch_id}/process")
def process_notification_batch(
    batch_id: int,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Process notification batch"""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    success = crud.process_notification_batch(db, batch_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to process batch")
    
    return {"message": "Batch processing started"}


# Notification Webhook Routes (Admin only)
@router.post("/webhooks", response_model=schemas.NotificationWebhookOut)
def create_notification_webhook(
    webhook_data: schemas.NotificationWebhookCreate,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Create notification webhook"""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return crud.create_notification_webhook(db, webhook_data)


@router.get("/webhooks", response_model=schemas.NotificationWebhookListResponse)
def get_notification_webhooks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get notification webhooks"""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    webhooks, total = crud.get_notification_webhooks(
        db=db,
        skip=skip,
        limit=limit,
        is_active=is_active
    )
    
    return schemas.NotificationWebhookListResponse(
        webhooks=webhooks,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/webhooks/{webhook_id}", response_model=schemas.NotificationWebhookOut)
def get_notification_webhook(
    webhook_id: int,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get notification webhook by ID"""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    webhook = crud.get_notification_webhook(db, webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    return webhook


@router.patch("/webhooks/{webhook_id}", response_model=schemas.NotificationWebhookOut)
def update_notification_webhook(
    webhook_id: int,
    webhook_data: schemas.NotificationWebhookUpdate,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Update notification webhook"""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    webhook = crud.update_notification_webhook(db, webhook_id, webhook_data)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    return webhook


@router.delete("/webhooks/{webhook_id}")
def delete_notification_webhook(
    webhook_id: int,
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Delete notification webhook"""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    success = crud.delete_notification_webhook(db, webhook_id)
    if not success:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    return {"message": "Webhook deleted successfully"}


# Notification Analytics Routes (Admin only)
@router.get("/analytics", response_model=schemas.NotificationAnalyticsListResponse)
def get_notification_analytics(
    start_date: datetime = Query(default_factory=lambda: datetime.utcnow() - timedelta(days=30)),
    end_date: datetime = Query(default_factory=lambda: datetime.utcnow()),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get notification analytics"""
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    analytics, total = crud.get_notification_analytics(
        db=db,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    
    return schemas.NotificationAnalyticsListResponse(
        analytics=analytics,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/analytics/summary", response_model=schemas.NotificationAnalyticsSummary)
def get_notification_analytics_summary(
    start_date: datetime = Query(default_factory=lambda: datetime.utcnow() - timedelta(days=30)),
    end_date: datetime = Query(default_factory=lambda: datetime.utcnow()),
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get notification analytics summary"""
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return crud.get_notification_analytics_summary(db, start_date, end_date)


@router.get("/analytics/performance", response_model=schemas.NotificationPerformanceMetrics)
def get_notification_performance_metrics(
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get notification performance metrics"""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return crud.get_notification_performance_metrics(db)


@router.get("/analytics/trends", response_model=List[schemas.NotificationTrends])
def get_notification_trends(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get notification trends over time"""
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return crud.get_notification_trends(db, days)


# Utility Routes
@router.post("/cleanup")
def cleanup_old_notifications(
    days: int = Query(90, ge=1, le=365),
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Clean up old notifications"""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    deleted_count = crud.cleanup_old_notifications(db, days)
    return {"message": f"Cleaned up {deleted_count} old notifications"}


@router.get("/stats")
def get_notification_stats(
    db: Session = Depends(db_dep),
    current_user: User = Depends(get_current_user)
):
    """Get notification statistics for current user"""
    notifications, total, unread_count = crud.get_user_notifications(
        db=db,
        user_id=current_user.id,
        skip=0,
        limit=1
    )
    
    return {
        "total_notifications": total,
        "unread_notifications": unread_count,
        "read_notifications": total - unread_count
    }


# Background task for sending notifications
async def send_notification_background(notification_id: int, db: Session):
    """Background task to send notifications"""
    # This would handle the actual sending logic
    # For now, just a placeholder
    pass


# Export the manager for use in other parts of the application
def get_connection_manager() -> ConnectionManager:
    return manager