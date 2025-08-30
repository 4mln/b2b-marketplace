"""
Mobile API Optimization Routes
FastAPI endpoints for mobile-optimized API functionality
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import json
import time

from app.db.session import get_db
from app.core.auth import get_current_user_sync as get_current_user, get_current_user_optional_sync as get_current_user_optional
from plugins.auth.models import User
from . import crud
from .schemas import (
    MobileAppSessionCreate, MobileAppSessionUpdate, MobileAppSessionOut,
    MobileAPICallCreate, MobileAPICallOut, APICacheCreate, APICacheUpdate, APICacheOut,
    MobileAppConfigCreate, MobileAppConfigUpdate, MobileAppConfigOut,
    MobileFeatureFlagCreate, MobileFeatureFlagUpdate, MobileFeatureFlagOut,
    MobilePerformanceMetricCreate, MobilePerformanceMetricOut,
    MobileOfflineQueueCreate, MobileOfflineQueueUpdate, MobileOfflineQueueOut,
    MobilePushNotificationCreate, MobilePushNotificationUpdate, MobilePushNotificationOut,
    MobileSyncStateCreate, MobileSyncStateUpdate, MobileSyncStateOut,
    MobileAPIAnalytics, MobilePerformanceSummary, MobileOfflineQueueSummary,
    MobilePushNotificationSummary, MobileHealthCheck, CacheRequest, CacheResponse,
    FeatureFlagRequest, FeatureFlagResponse, SyncRequest, SyncResponse,
    MobileSessionRequest, MobileSessionResponse, PerformanceMetricRequest,
    OfflineActionRequest, PushNotificationRequest, MobileAppSessionListResponse,
    MobileAPICallListResponse, APICacheListResponse, MobileAppConfigListResponse,
    MobileFeatureFlagListResponse, MobilePerformanceMetricListResponse,
    MobileOfflineQueueListResponse, MobilePushNotificationListResponse,
    MobileSyncStateListResponse, MobileOptimizationConfig
)

router = APIRouter(prefix="/mobile", tags=["mobile"])


# Mobile App Session Routes
@router.post("/sessions", response_model=MobileSessionResponse)
def create_mobile_session(
    session_request: MobileSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Create a new mobile app session"""
    session_data = MobileAppSessionCreate(**session_request.dict())
    session = crud.create_mobile_session(db, session_data, current_user.id if current_user else None)
    return MobileSessionResponse(
        session_id=session.session_id,
        user_id=session.user_id,
        is_active=session.is_active,
        last_activity=session.last_activity
    )


@router.get("/sessions/{session_id}", response_model=MobileAppSessionOut)
def get_mobile_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Get mobile session by ID"""
    session = crud.get_mobile_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Mobile session not found")
    return session


@router.put("/sessions/{session_id}", response_model=MobileAppSessionOut)
def update_mobile_session(
    session_id: str,
    session_data: MobileAppSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Update mobile session"""
    session = crud.update_mobile_session(db, session_id, session_data)
    if not session:
        raise HTTPException(status_code=404, detail="Mobile session not found")
    return session


@router.delete("/sessions/{session_id}")
def deactivate_mobile_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Deactivate mobile session"""
    success = crud.deactivate_mobile_session(db, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Mobile session not found")
    return {"message": "Session deactivated successfully"}


@router.get("/sessions", response_model=MobileAppSessionListResponse)
def get_user_mobile_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's mobile sessions"""
    sessions, total = crud.get_user_mobile_sessions(db, current_user.id, skip, limit)
    return MobileAppSessionListResponse(
        sessions=sessions,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


# API Cache Routes
@router.post("/cache", response_model=CacheResponse)
def create_cache_entry(
    cache_request: CacheRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Create cache entry"""
    cache_key = crud.generate_cache_key(
        cache_request.endpoint,
        cache_request.method,
        cache_request.request_data
    )
    request_hash = crud.generate_request_hash(
        cache_request.request_data,
        cache_request.headers
    )
    
    # For demo purposes, create a simple cached response
    cache_data = APICacheCreate(
        cache_key=cache_key,
        endpoint=cache_request.endpoint,
        method=cache_request.method,
        request_hash=request_hash,
        response_data={"cached": True, "data": "Sample cached response"},
        expires_at=datetime.utcnow() + timedelta(minutes=30)
    )
    
    cache_entry = crud.create_cache_entry(db, cache_data)
    return CacheResponse(
        cache_key=cache_entry.cache_key,
        response_data=cache_entry.response_data,
        response_headers=cache_entry.response_headers,
        content_type=cache_entry.content_type,
        compression_type=cache_entry.compression_type,
        cache_control=cache_entry.cache_control,
        expires_at=cache_entry.expires_at,
        hit_count=cache_entry.hit_count
    )


@router.get("/cache/{cache_key}", response_model=CacheResponse)
def get_cache_entry(
    cache_key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Get cache entry by key"""
    cache_entry = crud.get_cache_entry(db, cache_key)
    if not cache_entry:
        raise HTTPException(status_code=404, detail="Cache entry not found or expired")
    return CacheResponse(
        cache_key=cache_entry.cache_key,
        response_data=cache_entry.response_data,
        response_headers=cache_entry.response_headers,
        content_type=cache_entry.content_type,
        compression_type=cache_entry.compression_type,
        cache_control=cache_entry.cache_control,
        expires_at=cache_entry.expires_at,
        hit_count=cache_entry.hit_count
    )


@router.delete("/cache/{cache_key}")
def delete_cache_entry(
    cache_key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Delete cache entry"""
    success = crud.delete_cache_entry(db, cache_key)
    if not success:
        raise HTTPException(status_code=404, detail="Cache entry not found")
    return {"message": "Cache entry deleted successfully"}


@router.post("/cache/cleanup")
def cleanup_expired_cache(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Clean up expired cache entries"""
    deleted_count = crud.cleanup_expired_cache(db)
    return {"message": f"Cleaned up {deleted_count} expired cache entries"}


# Mobile App Configuration Routes
@router.post("/config", response_model=MobileAppConfigOut)
def create_app_config(
    config_data: MobileAppConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create mobile app configuration"""
    return crud.create_app_config(db, config_data)


@router.get("/config/{platform}/{app_version}", response_model=MobileAppConfigOut)
def get_app_config(
    platform: str,
    app_version: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Get app configuration for platform and version"""
    config = crud.get_app_config(db, platform, app_version)
    if not config:
        raise HTTPException(status_code=404, detail="App configuration not found")
    return config


@router.get("/config/{platform}/latest", response_model=MobileAppConfigOut)
def get_latest_app_config(
    platform: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Get latest app configuration for platform"""
    config = crud.get_latest_app_config(db, platform)
    if not config:
        raise HTTPException(status_code=404, detail="App configuration not found")
    return config


@router.put("/config/{config_id}", response_model=MobileAppConfigOut)
def update_app_config(
    config_id: int,
    config_data: MobileAppConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update app configuration"""
    config = crud.update_app_config(db, config_id, config_data)
    if not config:
        raise HTTPException(status_code=404, detail="App configuration not found")
    return config


# Feature Flag Routes
@router.post("/feature-flags", response_model=MobileFeatureFlagOut)
def create_feature_flag(
    flag_data: MobileFeatureFlagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create feature flag"""
    return crud.create_feature_flag(db, flag_data)


@router.get("/feature-flags/{feature_name}", response_model=FeatureFlagResponse)
def check_feature_flag(
    feature_name: str,
    user_id: Optional[int] = Query(None),
    app_version: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    user_segments: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Check if feature flag is enabled"""
    return crud.check_feature_flag(
        db, feature_name, user_id or (current_user.id if current_user else None),
        app_version, platform, user_segments
    )


@router.get("/feature-flags", response_model=MobileFeatureFlagListResponse)
def get_feature_flags(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get feature flags"""
    # This would need to be implemented in CRUD
    flags = []
    total = 0
    return MobileFeatureFlagListResponse(
        flags=flags,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.put("/feature-flags/{flag_id}", response_model=MobileFeatureFlagOut)
def update_feature_flag(
    flag_id: int,
    flag_data: MobileFeatureFlagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update feature flag"""
    flag = crud.update_feature_flag(db, flag_id, flag_data)
    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag not found")
    return flag


# Performance Metrics Routes
@router.post("/performance-metrics", response_model=MobilePerformanceMetricOut)
def create_performance_metric(
    metric_request: PerformanceMetricRequest,
    session_id: str = Query(..., description="Mobile session ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Create performance metric"""
    session = crud.get_mobile_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Mobile session not found")
    
    metric_data = MobilePerformanceMetricCreate(
        session_id=session.id,
        **metric_request.dict()
    )
    return crud.create_performance_metric(db, metric_data)


@router.get("/performance-metrics/{session_id}", response_model=MobilePerformanceMetricListResponse)
def get_session_performance_metrics(
    session_id: str,
    metric_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Get performance metrics for session"""
    session = crud.get_mobile_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Mobile session not found")
    
    metrics, total = crud.get_session_performance_metrics(
        db, session.id, metric_type, skip, limit
    )
    return MobilePerformanceMetricListResponse(
        metrics=metrics,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/performance/summary", response_model=MobilePerformanceSummary)
def get_performance_summary(
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get performance summary for date range"""
    return crud.get_performance_summary(db, start_date, end_date)


# Offline Queue Routes
@router.post("/offline-queue", response_model=MobileOfflineQueueOut)
def create_offline_action(
    action_request: OfflineActionRequest,
    session_id: str = Query(..., description="Mobile session ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Create offline action"""
    session = crud.get_mobile_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Mobile session not found")
    
    action_data = MobileOfflineQueueCreate(
        session_id=session.id,
        **action_request.dict()
    )
    return crud.create_offline_action(db, action_data)


@router.get("/offline-queue/{session_id}", response_model=MobileOfflineQueueListResponse)
def get_session_offline_actions(
    session_id: str,
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Get offline actions for session"""
    session = crud.get_mobile_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Mobile session not found")
    
    actions, total = crud.get_session_offline_actions(
        db, session.id, status, skip, limit
    )
    return MobileOfflineQueueListResponse(
        actions=actions,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.post("/offline-queue/{session_id}/process")
def process_offline_actions(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Process pending offline actions for session"""
    session = crud.get_mobile_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Mobile session not found")
    
    processed_actions = crud.process_offline_actions(db, session.id)
    return {"message": f"Processed {len(processed_actions)} actions", "actions": processed_actions}


@router.get("/offline-queue/summary", response_model=MobileOfflineQueueSummary)
def get_offline_queue_summary(
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get offline queue summary for date range"""
    return crud.get_offline_queue_summary(db, start_date, end_date)


# Push Notification Routes
@router.post("/push-notifications", response_model=MobilePushNotificationOut)
def create_push_notification(
    notification_request: PushNotificationRequest,
    session_id: str = Query(..., description="Mobile session ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Create push notification"""
    session = crud.get_mobile_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Mobile session not found")
    
    notification_data = MobilePushNotificationCreate(
        session_id=session.id,
        **notification_request.dict()
    )
    return crud.create_push_notification(db, notification_data)


@router.get("/push-notifications/{session_id}", response_model=MobilePushNotificationListResponse)
def get_session_push_notifications(
    session_id: str,
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Get push notifications for session"""
    session = crud.get_mobile_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Mobile session not found")
    
    notifications, total = crud.get_session_push_notifications(
        db, session.id, status, skip, limit
    )
    return MobilePushNotificationListResponse(
        notifications=notifications,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/push-notifications/summary", response_model=MobilePushNotificationSummary)
def get_push_notification_summary(
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get push notification summary for date range"""
    return crud.get_push_notification_summary(db, start_date, end_date)


# Sync State Routes
@router.post("/sync", response_model=SyncResponse)
def sync_data(
    sync_request: SyncRequest,
    session_id: str = Query(..., description="Mobile session ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Sync data for entity type"""
    session = crud.get_mobile_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Mobile session not found")
    
    return crud.sync_data(db, session.id, sync_request.entity_type, sync_request.sync_token)


@router.get("/sync/{session_id}/{entity_type}", response_model=MobileSyncStateOut)
def get_sync_state(
    session_id: str,
    entity_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Get sync state for session and entity type"""
    session = crud.get_mobile_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Mobile session not found")
    
    sync_state = crud.get_sync_state(db, session.id, entity_type)
    if not sync_state:
        raise HTTPException(status_code=404, detail="Sync state not found")
    return sync_state


# Analytics Routes
@router.get("/analytics/api", response_model=MobileAPIAnalytics)
def get_api_analytics(
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get API analytics for date range"""
    return crud.get_api_analytics(db, start_date, end_date)


# Health Check Routes
@router.get("/health/{session_id}", response_model=MobileHealthCheck)
def get_mobile_health_check(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Get mobile app health check"""
    return crud.get_mobile_health_check(db, session_id)


# Optimization Configuration Routes
@router.get("/optimization-config", response_model=MobileOptimizationConfig)
def get_optimization_config():
    """Get mobile optimization configuration"""
    return MobileOptimizationConfig()


# API Call Tracking Middleware
@router.middleware("http")
async def track_api_calls(request: Request, call_next):
    """Track API calls for mobile optimization"""
    start_time = time.time()
    
    # Get session ID from headers
    session_id = request.headers.get("X-Mobile-Session-ID")
    
    response = await call_next(request)
    
    # Calculate response time
    response_time_ms = int((time.time() - start_time) * 1000)
    
    # Track API call if session ID is provided
    if session_id:
        try:
            db = next(get_db())
            session = crud.get_mobile_session(db, session_id)
            if session:
                call_data = MobileAPICallCreate(
                    session_id=session.id,
                    endpoint=str(request.url.path),
                    method=request.method,
                    response_time_ms=response_time_ms,
                    status_code=response.status_code,
                    cache_hit=False,  # Would need to be determined by cache logic
                    compression_used="gzip" in response.headers.get("content-encoding", ""),
                    user_agent=request.headers.get("user-agent"),
                    ip_address=request.client.host if request.client else None
                )
                crud.create_api_call(db, call_data)
        except Exception as e:
            # Log error but don't fail the request
            print(f"Error tracking API call: {e}")
    
    return response


# Utility Routes
@router.post("/compress")
def compress_data_endpoint(
    data: str,
    compression_type: str = Query("gzip", description="Compression type")
):
    """Compress data"""
    compressed = crud.compress_data(data, compression_type)
    return {"compressed_data": compressed.hex()}


@router.post("/decompress")
def decompress_data_endpoint(
    compressed_data: str,
    compression_type: str = Query("gzip", description="Compression type")
):
    """Decompress data"""
    try:
        decompressed = crud.decompress_data(bytes.fromhex(compressed_data), compression_type)
        return {"decompressed_data": decompressed}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Decompression failed: {str(e)}")


@router.post("/cleanup/sessions")
def cleanup_inactive_sessions(
    days: int = Query(30, ge=1, le=365, description="Days to keep"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Clean up inactive sessions"""
    deleted_count = crud.cleanup_inactive_sessions(db, days)
    return {"message": f"Cleaned up {deleted_count} inactive sessions"}


# Mobile-specific API endpoints
@router.get("/products/optimized")
def get_optimized_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session_id: str = Query(..., description="Mobile session ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Get optimized product list for mobile"""
    # This would implement mobile-specific product optimization
    # For now, return a placeholder response
    return {
        "products": [],
        "total": 0,
        "page": skip // limit + 1,
        "size": limit,
        "optimized_for_mobile": True,
        "compression_used": True,
        "cache_hit": False
    }


@router.get("/search/optimized")
def get_optimized_search(
    query: str = Query(..., description="Search query"),
    session_id: str = Query(..., description="Mobile session ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Get optimized search results for mobile"""
    # This would implement mobile-specific search optimization
    return {
        "results": [],
        "query": query,
        "optimized_for_mobile": True,
        "compression_used": True,
        "cache_hit": False
    }


@router.get("/dashboard/mobile")
def get_mobile_dashboard(
    session_id: str = Query(..., description="Mobile session ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Get mobile-optimized dashboard data"""
    # This would implement mobile-specific dashboard optimization
    return {
        "dashboard": {
            "recent_orders": [],
            "favorite_products": [],
            "recommendations": [],
            "notifications": []
        },
        "optimized_for_mobile": True,
        "compression_used": True,
        "cache_hit": False
    }
