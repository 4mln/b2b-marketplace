"""
Mobile API Optimization Models
SQLAlchemy models for mobile-optimized API functionality
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.db.base import Base


class MobileAppSession(Base):
    """Mobile app session tracking"""
    __tablename__ = "mobile_app_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    device_id = Column(String(255), nullable=False)
    device_type = Column(String(50), nullable=False)  # ios, android, web
    app_version = Column(String(50), nullable=True)
    os_version = Column(String(50), nullable=True)
    device_model = Column(String(100), nullable=True)
    screen_resolution = Column(String(50), nullable=True)
    network_type = Column(String(50), nullable=True)  # wifi, cellular, etc.
    location_data = Column(JSON, nullable=True)
    push_token = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="mobile_sessions")
    api_calls = relationship("MobileAPICall", back_populates="session")


class MobileAPICall(Base):
    """Mobile API call tracking for optimization"""
    __tablename__ = "mobile_api_calls"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("mobile_app_sessions.id"), nullable=False)
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    request_size = Column(Integer, nullable=True)
    response_size = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    status_code = Column(Integer, nullable=False)
    cache_hit = Column(Boolean, default=False)
    compression_used = Column(Boolean, default=False)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("MobileAppSession", back_populates="api_calls")


class APICache(Base):
    """API response caching for mobile optimization"""
    __tablename__ = "api_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(255), unique=True, index=True, nullable=False)
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    request_hash = Column(String(64), nullable=False)
    response_data = Column(JSON, nullable=False)
    response_headers = Column(JSON, nullable=True)
    content_type = Column(String(100), nullable=True)
    compression_type = Column(String(20), nullable=True)  # gzip, brotli, etc.
    cache_control = Column(String(100), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    hit_count = Column(Integer, default=0)
    last_accessed = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class MobileAppConfig(Base):
    """Mobile app configuration and settings"""
    __tablename__ = "mobile_app_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    app_version = Column(String(50), nullable=False)
    platform = Column(String(20), nullable=False)  # ios, android
    config_data = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    min_version_required = Column(String(50), nullable=True)
    force_update = Column(Boolean, default=False)
    maintenance_mode = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class MobileFeatureFlag(Base):
    """Feature flags for mobile app A/B testing and gradual rollouts"""
    __tablename__ = "mobile_feature_flags"
    
    id = Column(Integer, primary_key=True, index=True)
    feature_name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    is_enabled = Column(Boolean, default=False)
    rollout_percentage = Column(Float, default=0.0)  # 0.0 to 1.0
    target_platforms = Column(JSON, nullable=True)  # ["ios", "android"]
    min_app_version = Column(String(50), nullable=True)
    max_app_version = Column(String(50), nullable=True)
    user_segments = Column(JSON, nullable=True)  # ["premium", "new_users", etc.]
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class MobilePerformanceMetric(Base):
    """Mobile app performance metrics"""
    __tablename__ = "mobile_performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("mobile_app_sessions.id"), nullable=False)
    metric_type = Column(String(50), nullable=False)  # app_startup, api_call, ui_render, etc.
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20), nullable=True)  # ms, MB, etc.
    extra_metadata = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("MobileAppSession")


class MobileOfflineQueue(Base):
    """Offline action queue for mobile apps"""
    __tablename__ = "mobile_offline_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("mobile_app_sessions.id"), nullable=False)
    action_type = Column(String(50), nullable=False)  # create_order, update_profile, etc.
    action_data = Column(JSON, nullable=False)
    priority = Column(Integer, default=0)  # Higher number = higher priority
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    session = relationship("MobileAppSession")


class MobilePushNotification(Base):
    """Mobile push notification tracking"""
    __tablename__ = "mobile_push_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("mobile_app_sessions.id"), nullable=False)
    notification_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    data = Column(JSON, nullable=True)
    push_token = Column(String(255), nullable=False)
    status = Column(String(20), default="pending")  # pending, sent, delivered, failed
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("MobileAppSession")


class MobileSyncState(Base):
    """Mobile app data synchronization state"""
    __tablename__ = "mobile_sync_states"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("mobile_app_sessions.id"), nullable=False)
    entity_type = Column(String(50), nullable=False)  # products, orders, user_profile, etc.
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    sync_token = Column(String(255), nullable=True)
    data_version = Column(String(50), nullable=True)
    is_syncing = Column(Boolean, default=False)
    sync_errors = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    session = relationship("MobileAppSession")


# Indexes for performance optimization
Index('idx_mobile_sessions_user_device', MobileAppSession.user_id, MobileAppSession.device_id)
Index('idx_mobile_sessions_active', MobileAppSession.is_active, MobileAppSession.last_activity)
Index('idx_api_calls_session_endpoint', MobileAPICall.session_id, MobileAPICall.endpoint)
Index('idx_api_calls_response_time', MobileAPICall.response_time_ms)
Index('idx_api_cache_endpoint_expires', APICache.endpoint, APICache.expires_at)
Index('idx_api_cache_key_expires', APICache.cache_key, APICache.expires_at)
Index('idx_mobile_config_platform_version', MobileAppConfig.platform, MobileAppConfig.app_version)
Index('idx_feature_flags_enabled', MobileFeatureFlag.is_enabled, MobileFeatureFlag.feature_name)
Index('idx_performance_metrics_session_type', MobilePerformanceMetric.session_id, MobilePerformanceMetric.metric_type)
Index('idx_offline_queue_session_status', MobileOfflineQueue.session_id, MobileOfflineQueue.status)
Index('idx_push_notifications_session_status', MobilePushNotification.session_id, MobilePushNotification.status)
Index('idx_sync_states_session_entity', MobileSyncState.session_id, MobileSyncState.entity_type)


