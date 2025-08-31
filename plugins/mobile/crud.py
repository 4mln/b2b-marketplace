"""
Mobile API Optimization CRUD Operations
Comprehensive mobile-optimized API functionality for the B2B marketplace
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc, text, case, extract
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import json
import hashlib
import uuid
import gzip
import brotli

from .models import (
    MobileAppSession, MobileAPICall, APICache, MobileAppConfig, MobileFeatureFlag,
    MobilePerformanceMetric, MobileOfflineQueue, MobilePushNotification, MobileSyncState
)
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
    FeatureFlagRequest, FeatureFlagResponse, SyncRequest, SyncResponse
)


# Mobile App Session CRUD Operations
def create_mobile_session(db: Session, session_data: MobileAppSessionCreate, user_id: Optional[int] = None) -> MobileAppSessionOut:
    """Create a new mobile app session"""
    session_id = str(uuid.uuid4())
    db_session = MobileAppSession(
        session_id=session_id,
        user_id=user_id,
        **session_data.dict()
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return MobileAppSessionOut.from_orm(db_session)


def get_mobile_session(db: Session, session_id: str) -> Optional[MobileAppSessionOut]:
    """Get mobile session by session ID"""
    db_session = db.query(MobileAppSession).filter(MobileAppSession.session_id == session_id).first()
    return MobileAppSessionOut.from_orm(db_session) if db_session else None


def get_user_mobile_sessions(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[MobileAppSessionOut], int]:
    """Get user's mobile sessions"""
    query = db.query(MobileAppSession).filter(MobileAppSession.user_id == user_id)
    total = query.count()
    sessions = query.order_by(desc(MobileAppSession.last_activity)).offset(skip).limit(limit).all()
    return [MobileAppSessionOut.from_orm(session) for session in sessions], total


def update_mobile_session(db: Session, session_id: str, session_data: MobileAppSessionUpdate) -> Optional[MobileAppSessionOut]:
    """Update mobile session"""
    db_session = db.query(MobileAppSession).filter(MobileAppSession.session_id == session_id).first()
    if not db_session:
        return None
    
    for field, value in session_data.dict(exclude_unset=True).items():
        setattr(db_session, field, value)
    
    db_session.last_activity = datetime.utcnow()
    db.commit()
    db.refresh(db_session)
    return MobileAppSessionOut.from_orm(db_session)


def deactivate_mobile_session(db: Session, session_id: str) -> bool:
    """Deactivate mobile session"""
    db_session = db.query(MobileAppSession).filter(MobileAppSession.session_id == session_id).first()
    if not db_session:
        return False
    
    db_session.is_active = False
    db.commit()
    return True


def cleanup_inactive_sessions(db: Session, days: int = 30) -> int:
    """Clean up inactive sessions older than specified days"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    deleted_count = db.query(MobileAppSession).filter(
        MobileAppSession.last_activity < cutoff_date,
        MobileAppSession.is_active == False
    ).delete()
    db.commit()
    return deleted_count


# Mobile API Call CRUD Operations
def create_api_call(db: Session, call_data: MobileAPICallCreate) -> MobileAPICallOut:
    """Create API call record"""
    db_call = MobileAPICall(**call_data.dict())
    db.add(db_call)
    db.commit()
    db.refresh(db_call)
    return MobileAPICallOut.from_orm(db_call)


def get_session_api_calls(
    db: Session,
    session_id: int,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[MobileAPICallOut], int]:
    """Get API calls for a session"""
    query = db.query(MobileAPICall).filter(MobileAPICall.session_id == session_id)
    total = query.count()
    calls = query.order_by(desc(MobileAPICall.created_at)).offset(skip).limit(limit).all()
    return [MobileAPICallOut.from_orm(call) for call in calls], total


def get_api_analytics(db: Session, start_date: datetime, end_date: datetime) -> MobileAPIAnalytics:
    """Get API analytics for date range"""
    # Total calls
    total_calls = db.query(func.count(MobileAPICall.id)).filter(
        MobileAPICall.created_at >= start_date,
        MobileAPICall.created_at <= end_date
    ).scalar() or 0
    
    # Average response time
    avg_response_time = db.query(func.avg(MobileAPICall.response_time_ms)).filter(
        MobileAPICall.created_at >= start_date,
        MobileAPICall.created_at <= end_date,
        MobileAPICall.response_time_ms.isnot(None)
    ).scalar() or 0.0
    
    # Cache hit rate
    cache_hits = db.query(func.count(MobileAPICall.id)).filter(
        MobileAPICall.created_at >= start_date,
        MobileAPICall.created_at <= end_date,
        MobileAPICall.cache_hit == True
    ).scalar() or 0
    cache_hit_rate = (cache_hits / total_calls * 100) if total_calls > 0 else 0.0
    
    # Compression usage rate
    compression_used = db.query(func.count(MobileAPICall.id)).filter(
        MobileAPICall.created_at >= start_date,
        MobileAPICall.created_at <= end_date,
        MobileAPICall.compression_used == True
    ).scalar() or 0
    compression_usage_rate = (compression_used / total_calls * 100) if total_calls > 0 else 0.0
    
    # Error rate
    errors = db.query(func.count(MobileAPICall.id)).filter(
        MobileAPICall.created_at >= start_date,
        MobileAPICall.created_at <= end_date,
        MobileAPICall.status_code >= 400
    ).scalar() or 0
    error_rate = (errors / total_calls * 100) if total_calls > 0 else 0.0
    
    # Top endpoints
    top_endpoints = db.query(
        MobileAPICall.endpoint,
        func.count(MobileAPICall.id).label('count'),
        func.avg(MobileAPICall.response_time_ms).label('avg_time')
    ).filter(
        MobileAPICall.created_at >= start_date,
        MobileAPICall.created_at <= end_date
    ).group_by(MobileAPICall.endpoint).order_by(desc('count')).limit(10).all()
    
    # Platform distribution
    platform_distribution = db.query(
        MobileAppSession.device_type,
        func.count(MobileAPICall.id).label('count')
    ).join(MobileAPICall).filter(
        MobileAPICall.created_at >= start_date,
        MobileAPICall.created_at <= end_date
    ).group_by(MobileAppSession.device_type).all()
    
    # Network distribution
    network_distribution = db.query(
        MobileAppSession.network_type,
        func.count(MobileAPICall.id).label('count')
    ).join(MobileAPICall).filter(
        MobileAPICall.created_at >= start_date,
        MobileAPICall.created_at <= end_date,
        MobileAppSession.network_type.isnot(None)
    ).group_by(MobileAppSession.network_type).all()
    
    return MobileAPIAnalytics(
        total_calls=total_calls,
        avg_response_time_ms=avg_response_time,
        cache_hit_rate=cache_hit_rate,
        compression_usage_rate=compression_usage_rate,
        error_rate=error_rate,
        top_endpoints=[{"endpoint": e.endpoint, "count": e.count, "avg_time": e.avg_time} for e in top_endpoints],
        platform_distribution={p.device_type: p.count for p in platform_distribution},
        network_distribution={n.network_type: n.count for n in network_distribution}
    )


# API Cache CRUD Operations
def create_cache_entry(db: Session, cache_data: APICacheCreate) -> APICacheOut:
    """Create cache entry"""
    db_cache = APICache(**cache_data.dict())
    db.add(db_cache)
    db.commit()
    db.refresh(db_cache)
    return APICacheOut.from_orm(db_cache)


def get_cache_entry(db: Session, cache_key: str) -> Optional[APICacheOut]:
    """Get cache entry by key"""
    db_cache = db.query(APICache).filter(
        APICache.cache_key == cache_key,
        APICache.expires_at > datetime.utcnow()
    ).first()
    
    if db_cache:
        # Update hit count and last accessed
        db_cache.hit_count += 1
        db_cache.last_accessed = datetime.utcnow()
        db.commit()
        db.refresh(db_cache)
    
    return APICacheOut.from_orm(db_cache) if db_cache else None


def find_cache_entry(db: Session, endpoint: str, method: str, request_hash: str) -> Optional[APICacheOut]:
    """Find cache entry by endpoint, method, and request hash"""
    db_cache = db.query(APICache).filter(
        APICache.endpoint == endpoint,
        APICache.method == method,
        APICache.request_hash == request_hash,
        APICache.expires_at > datetime.utcnow()
    ).first()
    
    if db_cache:
        # Update hit count and last accessed
        db_cache.hit_count += 1
        db_cache.last_accessed = datetime.utcnow()
        db.commit()
        db.refresh(db_cache)
    
    return APICacheOut.from_orm(db_cache) if db_cache else None


def update_cache_entry(db: Session, cache_id: int, cache_data: APICacheUpdate) -> Optional[APICacheOut]:
    """Update cache entry"""
    db_cache = db.query(APICache).filter(APICache.id == cache_id).first()
    if not db_cache:
        return None
    
    for field, value in cache_data.dict(exclude_unset=True).items():
        setattr(db_cache, field, value)
    
    db.commit()
    db.refresh(db_cache)
    return APICacheOut.from_orm(db_cache)


def delete_cache_entry(db: Session, cache_key: str) -> bool:
    """Delete cache entry"""
    db_cache = db.query(APICache).filter(APICache.cache_key == cache_key).first()
    if not db_cache:
        return False
    
    db.delete(db_cache)
    db.commit()
    return True


def cleanup_expired_cache(db: Session) -> int:
    """Clean up expired cache entries"""
    deleted_count = db.query(APICache).filter(APICache.expires_at <= datetime.utcnow()).delete()
    db.commit()
    return deleted_count


def generate_cache_key(endpoint: str, method: str, request_data: Optional[Dict[str, Any]] = None) -> str:
    """Generate cache key from endpoint, method, and request data"""
    key_data = f"{method}:{endpoint}"
    if request_data:
        key_data += f":{json.dumps(request_data, sort_keys=True)}"
    return hashlib.md5(key_data.encode()).hexdigest()


def generate_request_hash(request_data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> str:
    """Generate request hash from data and headers"""
    hash_data = {}
    if request_data:
        hash_data['data'] = request_data
    if headers:
        # Filter out headers that don't affect response
        filtered_headers = {k: v for k, v in headers.items() if k.lower() not in ['user-agent', 'authorization']}
        hash_data['headers'] = filtered_headers
    
    return hashlib.sha256(json.dumps(hash_data, sort_keys=True).encode()).hexdigest()


# Mobile App Config CRUD Operations
def create_app_config(db: Session, config_data: MobileAppConfigCreate) -> MobileAppConfigOut:
    """Create mobile app configuration"""
    db_config = MobileAppConfig(**config_data.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return MobileAppConfigOut.from_orm(db_config)


def get_app_config(db: Session, platform: str, app_version: str) -> Optional[MobileAppConfigOut]:
    """Get app configuration for platform and version"""
    db_config = db.query(MobileAppConfig).filter(
        MobileAppConfig.platform == platform,
        MobileAppConfig.app_version == app_version,
        MobileAppConfig.is_active == True
    ).first()
    return MobileAppConfigOut.from_orm(db_config) if db_config else None


def get_latest_app_config(db: Session, platform: str) -> Optional[MobileAppConfigOut]:
    """Get latest app configuration for platform"""
    db_config = db.query(MobileAppConfig).filter(
        MobileAppConfig.platform == platform,
        MobileAppConfig.is_active == True
    ).order_by(desc(MobileAppConfig.app_version)).first()
    return MobileAppConfigOut.from_orm(db_config) if db_config else None


def update_app_config(db: Session, config_id: int, config_data: MobileAppConfigUpdate) -> Optional[MobileAppConfigOut]:
    """Update app configuration"""
    db_config = db.query(MobileAppConfig).filter(MobileAppConfig.id == config_id).first()
    if not db_config:
        return None
    
    for field, value in config_data.dict(exclude_unset=True).items():
        setattr(db_config, field, value)
    
    db.commit()
    db.refresh(db_config)
    return MobileAppConfigOut.from_orm(db_config)


# Feature Flag CRUD Operations
def create_feature_flag(db: Session, flag_data: MobileFeatureFlagCreate) -> MobileFeatureFlagOut:
    """Create feature flag"""
    db_flag = MobileFeatureFlag(**flag_data.dict())
    db.add(db_flag)
    db.commit()
    db.refresh(db_flag)
    return MobileFeatureFlagOut.from_orm(db_flag)


def get_feature_flag(db: Session, feature_name: str) -> Optional[MobileFeatureFlagOut]:
    """Get feature flag by name"""
    db_flag = db.query(MobileFeatureFlag).filter(MobileFeatureFlag.feature_name == feature_name).first()
    return MobileFeatureFlagOut.from_orm(db_flag) if db_flag else None


def check_feature_flag(
    db: Session,
    feature_name: str,
    user_id: Optional[int] = None,
    app_version: Optional[str] = None,
    platform: Optional[str] = None,
    user_segments: Optional[List[str]] = None
) -> FeatureFlagResponse:
    """Check if feature flag is enabled for given context"""
    db_flag = db.query(MobileFeatureFlag).filter(MobileFeatureFlag.feature_name == feature_name).first()
    
    if not db_flag or not db_flag.is_enabled:
        return FeatureFlagResponse(
            feature_name=feature_name,
            is_enabled=False,
            rollout_percentage=0.0
        )
    
    # Check platform compatibility
    if db_flag.target_platforms and platform and platform not in db_flag.target_platforms:
        return FeatureFlagResponse(
            feature_name=feature_name,
            is_enabled=False,
            rollout_percentage=db_flag.rollout_percentage,
            target_platforms=db_flag.target_platforms
        )
    
    # Check version compatibility
    if db_flag.min_app_version and app_version and app_version < db_flag.min_app_version:
        return FeatureFlagResponse(
            feature_name=feature_name,
            is_enabled=False,
            rollout_percentage=db_flag.rollout_percentage,
            min_app_version=db_flag.min_app_version
        )
    
    if db_flag.max_app_version and app_version and app_version > db_flag.max_app_version:
        return FeatureFlagResponse(
            feature_name=feature_name,
            is_enabled=False,
            rollout_percentage=db_flag.rollout_percentage,
            max_app_version=db_flag.max_app_version
        )
    
    # Check user segments
    if db_flag.user_segments and user_segments:
        if not any(segment in db_flag.user_segments for segment in user_segments):
            return FeatureFlagResponse(
                feature_name=feature_name,
                is_enabled=False,
                rollout_percentage=db_flag.rollout_percentage,
                user_segments=db_flag.user_segments
            )
    
    # Check rollout percentage (simple hash-based approach)
    if db_flag.rollout_percentage < 1.0 and user_id:
        user_hash = hash(str(user_id)) % 100
        if user_hash >= db_flag.rollout_percentage * 100:
            return FeatureFlagResponse(
                feature_name=feature_name,
                is_enabled=False,
                rollout_percentage=db_flag.rollout_percentage
            )
    
    return FeatureFlagResponse(
        feature_name=feature_name,
        is_enabled=True,
        rollout_percentage=db_flag.rollout_percentage,
        target_platforms=db_flag.target_platforms,
        min_app_version=db_flag.min_app_version,
        max_app_version=db_flag.max_app_version,
        user_segments=db_flag.user_segments
    )


def update_feature_flag(db: Session, flag_id: int, flag_data: MobileFeatureFlagUpdate) -> Optional[MobileFeatureFlagOut]:
    """Update feature flag"""
    db_flag = db.query(MobileFeatureFlag).filter(MobileFeatureFlag.id == flag_id).first()
    if not db_flag:
        return None
    
    for field, value in flag_data.dict(exclude_unset=True).items():
        setattr(db_flag, field, value)
    
    db.commit()
    db.refresh(db_flag)
    return MobileFeatureFlagOut.from_orm(db_flag)


# Performance Metrics CRUD Operations
def create_performance_metric(db: Session, metric_data: MobilePerformanceMetricCreate) -> MobilePerformanceMetricOut:
    """Create performance metric"""
    db_metric = MobilePerformanceMetric(**metric_data.dict())
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return MobilePerformanceMetricOut.from_orm(db_metric)


def get_session_performance_metrics(
    db: Session,
    session_id: int,
    metric_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[MobilePerformanceMetricOut], int]:
    """Get performance metrics for session"""
    query = db.query(MobilePerformanceMetric).filter(MobilePerformanceMetric.session_id == session_id)
    
    if metric_type:
        query = query.filter(MobilePerformanceMetric.metric_type == metric_type)
    
    total = query.count()
    metrics = query.order_by(desc(MobilePerformanceMetric.created_at)).offset(skip).limit(limit).all()
    return [MobilePerformanceMetricOut.from_orm(metric) for metric in metrics], total


def get_performance_summary(db: Session, start_date: datetime, end_date: datetime) -> MobilePerformanceSummary:
    """Get performance summary for date range"""
    # App startup time
    startup_metrics = db.query(func.avg(MobilePerformanceMetric.metric_value)).filter(
        MobilePerformanceMetric.metric_type == "app_startup",
        MobilePerformanceMetric.created_at >= start_date,
        MobilePerformanceMetric.created_at <= end_date
    ).scalar() or 0.0
    
    # API response time
    api_metrics = db.query(func.avg(MobilePerformanceMetric.metric_value)).filter(
        MobilePerformanceMetric.metric_type == "api_call",
        MobilePerformanceMetric.created_at >= start_date,
        MobilePerformanceMetric.created_at <= end_date
    ).scalar() or 0.0
    
    # UI render time
    ui_metrics = db.query(func.avg(MobilePerformanceMetric.metric_value)).filter(
        MobilePerformanceMetric.metric_type == "ui_render",
        MobilePerformanceMetric.created_at >= start_date,
        MobilePerformanceMetric.created_at <= end_date
    ).scalar() or 0.0
    
    # Memory usage
    memory_metrics = db.query(func.avg(MobilePerformanceMetric.metric_value)).filter(
        MobilePerformanceMetric.metric_type == "memory_usage",
        MobilePerformanceMetric.created_at >= start_date,
        MobilePerformanceMetric.created_at <= end_date
    ).scalar() or 0.0
    
    # Battery usage
    battery_metrics = db.query(func.avg(MobilePerformanceMetric.metric_value)).filter(
        MobilePerformanceMetric.metric_type == "battery_usage",
        MobilePerformanceMetric.created_at >= start_date,
        MobilePerformanceMetric.created_at <= end_date
    ).scalar() or 0.0
    
    # Crash rate (simplified calculation)
    total_sessions = db.query(func.count(MobileAppSession.id)).filter(
        MobileAppSession.created_at >= start_date,
        MobileAppSession.created_at <= end_date
    ).scalar() or 1
    
    crash_metrics = db.query(func.count(MobilePerformanceMetric.id)).filter(
        MobilePerformanceMetric.metric_type == "crash",
        MobilePerformanceMetric.created_at >= start_date,
        MobilePerformanceMetric.created_at <= end_date
    ).scalar() or 0
    
    crash_rate = (crash_metrics / total_sessions * 100) if total_sessions > 0 else 0.0
    
    # Session duration
    session_duration = db.query(func.avg(
        extract('epoch', MobileAppSession.last_activity - MobileAppSession.created_at)
    )).filter(
        MobileAppSession.created_at >= start_date,
        MobileAppSession.created_at <= end_date
    ).scalar() or 0.0
    
    return MobilePerformanceSummary(
        avg_app_startup_time=startup_metrics,
        avg_api_response_time=api_metrics,
        avg_ui_render_time=ui_metrics,
        memory_usage_avg=memory_metrics,
        battery_usage_avg=battery_metrics,
        crash_rate=crash_rate,
        session_duration_avg=session_duration
    )


# Offline Queue CRUD Operations
def create_offline_action(db: Session, action_data: MobileOfflineQueueCreate) -> MobileOfflineQueueOut:
    """Create offline action"""
    db_action = MobileOfflineQueue(**action_data.dict())
    db.add(db_action)
    db.commit()
    db.refresh(db_action)
    return MobileOfflineQueueOut.from_orm(db_action)


def get_session_offline_actions(
    db: Session,
    session_id: int,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[MobileOfflineQueueOut], int]:
    """Get offline actions for session"""
    query = db.query(MobileOfflineQueue).filter(MobileOfflineQueue.session_id == session_id)
    
    if status:
        query = query.filter(MobileOfflineQueue.status == status)
    
    total = query.count()
    actions = query.order_by(desc(MobileOfflineQueue.priority), asc(MobileOfflineQueue.created_at)).offset(skip).limit(limit).all()
    return [MobileOfflineQueueOut.from_orm(action) for action in actions], total


def update_offline_action(db: Session, action_id: int, action_data: MobileOfflineQueueUpdate) -> Optional[MobileOfflineQueueOut]:
    """Update offline action"""
    db_action = db.query(MobileOfflineQueue).filter(MobileOfflineQueue.id == action_id).first()
    if not db_action:
        return None
    
    for field, value in action_data.dict(exclude_unset=True).items():
        setattr(db_action, field, value)
    
    db.commit()
    db.refresh(db_action)
    return MobileOfflineQueueOut.from_orm(db_action)


def process_offline_actions(db: Session, session_id: int) -> List[MobileOfflineQueueOut]:
    """Process pending offline actions for session"""
    pending_actions = db.query(MobileOfflineQueue).filter(
        MobileOfflineQueue.session_id == session_id,
        MobileOfflineQueue.status == "pending"
    ).order_by(desc(MobileOfflineQueue.priority), asc(MobileOfflineQueue.created_at)).all()
    
    processed_actions = []
    for action in pending_actions:
        try:
            # Mark as processing
            action.status = "processing"
            db.commit()
            
            # Here you would implement the actual action processing logic
            # For now, we'll just mark as completed
            action.status = "completed"
            action.processed_at = datetime.utcnow()
            db.commit()
            
            processed_actions.append(MobileOfflineQueueOut.from_orm(action))
        except Exception as e:
            action.status = "failed"
            action.error_message = str(e)
            action.retry_count += 1
            db.commit()
    
    return processed_actions


def get_offline_queue_summary(db: Session, start_date: datetime, end_date: datetime) -> MobileOfflineQueueSummary:
    """Get offline queue summary for date range"""
    # Count by status
    pending = db.query(func.count(MobileOfflineQueue.id)).filter(
        MobileOfflineQueue.created_at >= start_date,
        MobileOfflineQueue.created_at <= end_date,
        MobileOfflineQueue.status == "pending"
    ).scalar() or 0
    
    processing = db.query(func.count(MobileOfflineQueue.id)).filter(
        MobileOfflineQueue.created_at >= start_date,
        MobileOfflineQueue.created_at <= end_date,
        MobileOfflineQueue.status == "processing"
    ).scalar() or 0
    
    completed = db.query(func.count(MobileOfflineQueue.id)).filter(
        MobileOfflineQueue.created_at >= start_date,
        MobileOfflineQueue.created_at <= end_date,
        MobileOfflineQueue.status == "completed"
    ).scalar() or 0
    
    failed = db.query(func.count(MobileOfflineQueue.id)).filter(
        MobileOfflineQueue.created_at >= start_date,
        MobileOfflineQueue.created_at <= end_date,
        MobileOfflineQueue.status == "failed"
    ).scalar() or 0
    
    # Average processing time
    avg_processing_time = db.query(func.avg(
        extract('epoch', MobileOfflineQueue.processed_at - MobileOfflineQueue.created_at)
    )).filter(
        MobileOfflineQueue.created_at >= start_date,
        MobileOfflineQueue.created_at <= end_date,
        MobileOfflineQueue.status == "completed",
        MobileOfflineQueue.processed_at.isnot(None)
    ).scalar() or 0.0
    
    # Top action types
    top_actions = db.query(
        MobileOfflineQueue.action_type,
        func.count(MobileOfflineQueue.id).label('count')
    ).filter(
        MobileOfflineQueue.created_at >= start_date,
        MobileOfflineQueue.created_at <= end_date
    ).group_by(MobileOfflineQueue.action_type).order_by(desc('count')).limit(10).all()
    
    # Retry distribution
    retry_distribution = db.query(
        MobileOfflineQueue.retry_count,
        func.count(MobileOfflineQueue.id).label('count')
    ).filter(
        MobileOfflineQueue.created_at >= start_date,
        MobileOfflineQueue.created_at <= end_date
    ).group_by(MobileOfflineQueue.retry_count).all()
    
    return MobileOfflineQueueSummary(
        total_pending=pending,
        total_processing=processing,
        total_completed=completed,
        total_failed=failed,
        avg_processing_time=avg_processing_time,
        top_action_types=[{"action_type": a.action_type, "count": a.count} for a in top_actions],
        retry_distribution={r.retry_count: r.count for r in retry_distribution}
    )


# Push Notification CRUD Operations
def create_push_notification(db: Session, notification_data: MobilePushNotificationCreate) -> MobilePushNotificationOut:
    """Create push notification"""
    db_notification = MobilePushNotification(**notification_data.dict())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return MobilePushNotificationOut.from_orm(db_notification)


def get_session_push_notifications(
    db: Session,
    session_id: int,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[MobilePushNotificationOut], int]:
    """Get push notifications for session"""
    query = db.query(MobilePushNotification).filter(MobilePushNotification.session_id == session_id)
    
    if status:
        query = query.filter(MobilePushNotification.status == status)
    
    total = query.count()
    notifications = query.order_by(desc(MobilePushNotification.created_at)).offset(skip).limit(limit).all()
    return [MobilePushNotificationOut.from_orm(notification) for notification in notifications], total


def update_push_notification(db: Session, notification_id: int, notification_data: MobilePushNotificationUpdate) -> Optional[MobilePushNotificationOut]:
    """Update push notification"""
    db_notification = db.query(MobilePushNotification).filter(MobilePushNotification.id == notification_id).first()
    if not db_notification:
        return None
    
    for field, value in notification_data.dict(exclude_unset=True).items():
        setattr(db_notification, field, value)
    
    db.commit()
    db.refresh(db_notification)
    return MobilePushNotificationOut.from_orm(db_notification)


def get_push_notification_summary(db: Session, start_date: datetime, end_date: datetime) -> MobilePushNotificationSummary:
    """Get push notification summary for date range"""
    # Count by status
    sent = db.query(func.count(MobilePushNotification.id)).filter(
        MobilePushNotification.created_at >= start_date,
        MobilePushNotification.created_at <= end_date,
        MobilePushNotification.status == "sent"
    ).scalar() or 0
    
    delivered = db.query(func.count(MobilePushNotification.id)).filter(
        MobilePushNotification.created_at >= start_date,
        MobilePushNotification.created_at <= end_date,
        MobilePushNotification.status == "delivered"
    ).scalar() or 0
    
    failed = db.query(func.count(MobilePushNotification.id)).filter(
        MobilePushNotification.created_at >= start_date,
        MobilePushNotification.created_at <= end_date,
        MobilePushNotification.status == "failed"
    ).scalar() or 0
    
    total = sent + delivered + failed
    delivery_rate = (delivered / total * 100) if total > 0 else 0.0
    
    # Average delivery time
    avg_delivery_time = db.query(func.avg(
        extract('epoch', MobilePushNotification.delivered_at - MobilePushNotification.sent_at)
    )).filter(
        MobilePushNotification.created_at >= start_date,
        MobilePushNotification.created_at <= end_date,
        MobilePushNotification.status == "delivered",
        MobilePushNotification.sent_at.isnot(None),
        MobilePushNotification.delivered_at.isnot(None)
    ).scalar() or 0.0
    
    # Top notification types
    top_types = db.query(
        MobilePushNotification.notification_type,
        func.count(MobilePushNotification.id).label('count')
    ).filter(
        MobilePushNotification.created_at >= start_date,
        MobilePushNotification.created_at <= end_date
    ).group_by(MobilePushNotification.notification_type).order_by(desc('count')).limit(10).all()
    
    # Platform distribution
    platform_distribution = db.query(
        MobileAppSession.device_type,
        func.count(MobilePushNotification.id).label('count')
    ).join(MobilePushNotification).filter(
        MobilePushNotification.created_at >= start_date,
        MobilePushNotification.created_at <= end_date
    ).group_by(MobileAppSession.device_type).all()
    
    return MobilePushNotificationSummary(
        total_sent=sent,
        total_delivered=delivered,
        total_failed=failed,
        delivery_rate=delivery_rate,
        avg_delivery_time=avg_delivery_time,
        top_notification_types=[{"type": t.notification_type, "count": t.count} for t in top_types],
        platform_distribution={p.device_type: p.count for p in platform_distribution}
    )


# Sync State CRUD Operations
def create_sync_state(db: Session, sync_data: MobileSyncStateCreate) -> MobileSyncStateOut:
    """Create sync state"""
    db_sync = MobileSyncState(**sync_data.dict())
    db.add(db_sync)
    db.commit()
    db.refresh(db_sync)
    return MobileSyncStateOut.from_orm(db_sync)


def get_sync_state(db: Session, session_id: int, entity_type: str) -> Optional[MobileSyncStateOut]:
    """Get sync state for session and entity type"""
    db_sync = db.query(MobileSyncState).filter(
        MobileSyncState.session_id == session_id,
        MobileSyncState.entity_type == entity_type
    ).first()
    return MobileSyncStateOut.from_orm(db_sync) if db_sync else None


def update_sync_state(db: Session, sync_id: int, sync_data: MobileSyncStateUpdate) -> Optional[MobileSyncStateOut]:
    """Update sync state"""
    db_sync = db.query(MobileSyncState).filter(MobileSyncState.id == sync_id).first()
    if not db_sync:
        return None
    
    for field, value in sync_data.dict(exclude_unset=True).items():
        setattr(db_sync, field, value)
    
    db.commit()
    db.refresh(db_sync)
    return MobileSyncStateOut.from_orm(db_sync)


def sync_data(db: Session, session_id: int, entity_type: str, sync_token: Optional[str] = None) -> SyncResponse:
    """Sync data for entity type"""
    # Get or create sync state
    db_sync = db.query(MobileSyncState).filter(
        MobileSyncState.session_id == session_id,
        MobileSyncState.entity_type == entity_type
    ).first()
    
    if not db_sync:
        db_sync = MobileSyncState(
            session_id=session_id,
            entity_type=entity_type,
            sync_token=str(uuid.uuid4()),
            data_version="1.0"
        )
        db.add(db_sync)
    
    # Update sync state
    db_sync.is_syncing = True
    db_sync.last_sync_at = datetime.utcnow()
    if sync_token:
        db_sync.sync_token = sync_token
    
    try:
        # Here you would implement the actual sync logic
        # For now, we'll just update the data version
        db_sync.data_version = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        db_sync.is_syncing = False
        db.commit()
        
        return SyncResponse(
            entity_type=entity_type,
            sync_token=db_sync.sync_token,
            data_version=db_sync.data_version,
            last_sync_at=db_sync.last_sync_at,
            is_syncing=db_sync.is_syncing,
            sync_errors=None
        )
    except Exception as e:
        db_sync.is_syncing = False
        db_sync.sync_errors = {"error": str(e)}
        db.commit()
        
        return SyncResponse(
            entity_type=entity_type,
            sync_token=db_sync.sync_token or "",
            data_version=db_sync.data_version or "1.0",
            last_sync_at=db_sync.last_sync_at,
            is_syncing=db_sync.is_syncing,
            sync_errors=db_sync.sync_errors
        )


# Utility Functions
def compress_data(data: str, compression_type: str = "gzip") -> bytes:
    """Compress data using specified compression type"""
    if compression_type == "gzip":
        return gzip.compress(data.encode('utf-8'))
    elif compression_type == "brotli":
        return brotli.compress(data.encode('utf-8'))
    else:
        return data.encode('utf-8')


def decompress_data(data: bytes, compression_type: str = "gzip") -> str:
    """Decompress data using specified compression type"""
    if compression_type == "gzip":
        return gzip.decompress(data).decode('utf-8')
    elif compression_type == "brotli":
        return brotli.decompress(data).decode('utf-8')
    else:
        return data.decode('utf-8')


def get_mobile_health_check(db: Session, session_id: str) -> MobileHealthCheck:
    """Get mobile app health check"""
    # Check session
    session = get_mobile_session(db, session_id)
    session_active = session.is_active if session else False
    
    # Check cache health
    cache_healthy = True  # Simplified check
    
    # Check offline queue health
    if session:
        pending_actions = db.query(MobileOfflineQueue).filter(
            MobileOfflineQueue.session_id == session.id,
            MobileOfflineQueue.status == "failed",
            MobileOfflineQueue.retry_count >= 3
        ).count()
        offline_queue_healthy = pending_actions == 0
    else:
        offline_queue_healthy = False
    
    # Check push notifications health
    push_notifications_healthy = True  # Simplified check
    
    # Check sync health
    if session:
        failed_syncs = db.query(MobileSyncState).filter(
            MobileSyncState.session_id == session.id,
            MobileSyncState.sync_errors.isnot(None)
        ).count()
        sync_healthy = failed_syncs == 0
    else:
        sync_healthy = False
    
    # Check performance metrics health
    performance_metrics_healthy = True  # Simplified check
    
    # Overall status
    overall_status = "healthy" if all([
        session_active, cache_healthy, offline_queue_healthy,
        push_notifications_healthy, sync_healthy, performance_metrics_healthy
    ]) else "degraded"
    
    return MobileHealthCheck(
        session_active=session_active,
        cache_healthy=cache_healthy,
        offline_queue_healthy=offline_queue_healthy,
        push_notifications_healthy=push_notifications_healthy,
        sync_healthy=sync_healthy,
        performance_metrics_healthy=performance_metrics_healthy,
        overall_status=overall_status,
        last_check=datetime.utcnow()
    )


