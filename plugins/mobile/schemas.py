"""
Mobile API Optimization Schemas
Pydantic schemas for mobile-optimized API functionality
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


# Enums
class DeviceType(str, Enum):
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"


class NetworkType(str, Enum):
    WIFI = "wifi"
    CELLULAR = "cellular"
    ETHERNET = "ethernet"
    UNKNOWN = "unknown"


class CompressionType(str, Enum):
    GZIP = "gzip"
    BROTLI = "brotli"
    DEFLATE = "deflate"
    NONE = "none"


class QueueStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PushStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"


class SyncStatus(str, Enum):
    SYNCING = "syncing"
    SYNCED = "synced"
    FAILED = "failed"
    PENDING = "pending"


# Base Models
class MobileAppSessionBase(BaseModel):
    device_id: str = Field(..., description="Unique device identifier")
    device_type: DeviceType = Field(..., description="Device platform")
    app_version: Optional[str] = Field(None, description="App version")
    os_version: Optional[str] = Field(None, description="Operating system version")
    device_model: Optional[str] = Field(None, description="Device model")
    screen_resolution: Optional[str] = Field(None, description="Screen resolution")
    network_type: Optional[NetworkType] = Field(None, description="Network connection type")
    location_data: Optional[Dict[str, Any]] = Field(None, description="Location information")
    push_token: Optional[str] = Field(None, description="Push notification token")


class MobileAppSessionCreate(MobileAppSessionBase):
    pass


class MobileAppSessionUpdate(BaseModel):
    app_version: Optional[str] = None
    os_version: Optional[str] = None
    network_type: Optional[NetworkType] = None
    location_data: Optional[Dict[str, Any]] = None
    push_token: Optional[str] = None
    is_active: Optional[bool] = None


class MobileAppSessionOut(MobileAppSessionBase):
    id: int
    session_id: str
    user_id: Optional[int] = None
    is_active: bool
    last_activity: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# API Call Models
class MobileAPICallBase(BaseModel):
    endpoint: str = Field(..., description="API endpoint")
    method: str = Field(..., description="HTTP method")
    request_size: Optional[int] = Field(None, description="Request size in bytes")
    response_size: Optional[int] = Field(None, description="Response size in bytes")
    response_time_ms: Optional[int] = Field(None, description="Response time in milliseconds")
    status_code: int = Field(..., description="HTTP status code")
    cache_hit: bool = Field(False, description="Whether response was served from cache")
    compression_used: bool = Field(False, description="Whether compression was used")
    user_agent: Optional[str] = Field(None, description="User agent string")
    ip_address: Optional[str] = Field(None, description="Client IP address")


class MobileAPICallCreate(MobileAPICallBase):
    session_id: int


class MobileAPICallOut(MobileAPICallBase):
    id: int
    session_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Cache Models
class APICacheBase(BaseModel):
    endpoint: str = Field(..., description="API endpoint")
    method: str = Field(..., description="HTTP method")
    request_hash: str = Field(..., description="Hash of request parameters")
    response_data: Dict[str, Any] = Field(..., description="Cached response data")
    response_headers: Optional[Dict[str, Any]] = Field(None, description="Response headers")
    content_type: Optional[str] = Field(None, description="Content type")
    compression_type: Optional[CompressionType] = Field(None, description="Compression type used")
    cache_control: Optional[str] = Field(None, description="Cache control header")
    expires_at: datetime = Field(..., description="Cache expiration time")


class APICacheCreate(APICacheBase):
    cache_key: str = Field(..., description="Unique cache key")


class APICacheUpdate(BaseModel):
    response_data: Optional[Dict[str, Any]] = None
    response_headers: Optional[Dict[str, Any]] = None
    compression_type: Optional[CompressionType] = None
    cache_control: Optional[str] = None
    expires_at: Optional[datetime] = None


class APICacheOut(APICacheBase):
    id: int
    cache_key: str
    hit_count: int
    last_accessed: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# App Configuration Models
class MobileAppConfigBase(BaseModel):
    app_version: str = Field(..., description="App version")
    platform: str = Field(..., description="Platform (ios/android)")
    config_data: Dict[str, Any] = Field(..., description="Configuration data")
    min_version_required: Optional[str] = Field(None, description="Minimum required version")
    force_update: bool = Field(False, description="Force app update")
    maintenance_mode: bool = Field(False, description="Maintenance mode flag")


class MobileAppConfigCreate(MobileAppConfigBase):
    pass


class MobileAppConfigUpdate(BaseModel):
    config_data: Optional[Dict[str, Any]] = None
    min_version_required: Optional[str] = None
    force_update: Optional[bool] = None
    maintenance_mode: Optional[bool] = None
    is_active: Optional[bool] = None


class MobileAppConfigOut(MobileAppConfigBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Feature Flag Models
class MobileFeatureFlagBase(BaseModel):
    feature_name: str = Field(..., description="Feature name")
    description: Optional[str] = Field(None, description="Feature description")
    is_enabled: bool = Field(False, description="Feature enabled flag")
    rollout_percentage: float = Field(0.0, ge=0.0, le=1.0, description="Rollout percentage")
    target_platforms: Optional[List[str]] = Field(None, description="Target platforms")
    min_app_version: Optional[str] = Field(None, description="Minimum app version")
    max_app_version: Optional[str] = Field(None, description="Maximum app version")
    user_segments: Optional[List[str]] = Field(None, description="Target user segments")


class MobileFeatureFlagCreate(MobileFeatureFlagBase):
    pass


class MobileFeatureFlagUpdate(BaseModel):
    description: Optional[str] = None
    is_enabled: Optional[bool] = None
    rollout_percentage: Optional[float] = Field(None, ge=0.0, le=1.0)
    target_platforms: Optional[List[str]] = None
    min_app_version: Optional[str] = None
    max_app_version: Optional[str] = None
    user_segments: Optional[List[str]] = None


class MobileFeatureFlagOut(MobileFeatureFlagBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Performance Metrics Models
class MobilePerformanceMetricBase(BaseModel):
    metric_type: str = Field(..., description="Metric type")
    metric_name: str = Field(..., description="Metric name")
    metric_value: float = Field(..., description="Metric value")
    metric_unit: Optional[str] = Field(None, description="Metric unit")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class MobilePerformanceMetricCreate(MobilePerformanceMetricBase):
    session_id: int


class MobilePerformanceMetricOut(MobilePerformanceMetricBase):
    id: int
    session_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Offline Queue Models
class MobileOfflineQueueBase(BaseModel):
    action_type: str = Field(..., description="Action type")
    action_data: Dict[str, Any] = Field(..., description="Action data")
    priority: int = Field(0, ge=0, description="Priority level")
    max_retries: int = Field(3, ge=0, description="Maximum retry attempts")


class MobileOfflineQueueCreate(MobileOfflineQueueBase):
    session_id: int


class MobileOfflineQueueUpdate(BaseModel):
    action_data: Optional[Dict[str, Any]] = None
    priority: Optional[int] = Field(None, ge=0)
    status: Optional[QueueStatus] = None
    error_message: Optional[str] = None
    processed_at: Optional[datetime] = None


class MobileOfflineQueueOut(MobileOfflineQueueBase):
    id: int
    session_id: int
    retry_count: int
    status: QueueStatus
    error_message: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Push Notification Models
class MobilePushNotificationBase(BaseModel):
    notification_type: str = Field(..., description="Notification type")
    title: str = Field(..., description="Notification title")
    body: str = Field(..., description="Notification body")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")
    push_token: str = Field(..., description="Push notification token")


class MobilePushNotificationCreate(MobilePushNotificationBase):
    session_id: int


class MobilePushNotificationUpdate(BaseModel):
    status: Optional[PushStatus] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None


class MobilePushNotificationOut(MobilePushNotificationBase):
    id: int
    session_id: int
    status: PushStatus
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Sync State Models
class MobileSyncStateBase(BaseModel):
    entity_type: str = Field(..., description="Entity type")
    sync_token: Optional[str] = Field(None, description="Sync token")
    data_version: Optional[str] = Field(None, description="Data version")


class MobileSyncStateCreate(MobileSyncStateBase):
    session_id: int


class MobileSyncStateUpdate(BaseModel):
    last_sync_at: Optional[datetime] = None
    sync_token: Optional[str] = None
    data_version: Optional[str] = None
    is_syncing: Optional[bool] = None
    sync_errors: Optional[Dict[str, Any]] = None


class MobileSyncStateOut(MobileSyncStateBase):
    id: int
    session_id: int
    last_sync_at: Optional[datetime] = None
    is_syncing: bool
    sync_errors: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Request/Response Models
class MobileSessionRequest(BaseModel):
    device_id: str
    device_type: DeviceType
    app_version: Optional[str] = None
    os_version: Optional[str] = None
    device_model: Optional[str] = None
    screen_resolution: Optional[str] = None
    network_type: Optional[NetworkType] = None
    location_data: Optional[Dict[str, Any]] = None
    push_token: Optional[str] = None


class MobileSessionResponse(BaseModel):
    session_id: str
    user_id: Optional[int] = None
    is_active: bool
    last_activity: datetime


class CacheRequest(BaseModel):
    endpoint: str
    method: str
    request_data: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None


class CacheResponse(BaseModel):
    cache_key: str
    response_data: Dict[str, Any]
    response_headers: Optional[Dict[str, Any]] = None
    content_type: Optional[str] = None
    compression_type: Optional[CompressionType] = None
    cache_control: Optional[str] = None
    expires_at: datetime
    hit_count: int


class FeatureFlagRequest(BaseModel):
    feature_name: str
    user_id: Optional[int] = None
    app_version: Optional[str] = None
    platform: Optional[str] = None
    user_segments: Optional[List[str]] = None


class FeatureFlagResponse(BaseModel):
    feature_name: str
    is_enabled: bool
    rollout_percentage: float
    target_platforms: Optional[List[str]] = None
    min_app_version: Optional[str] = None
    max_app_version: Optional[str] = None
    user_segments: Optional[List[str]] = None


class PerformanceMetricRequest(BaseModel):
    metric_type: str
    metric_name: str
    metric_value: float
    metric_unit: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class OfflineActionRequest(BaseModel):
    action_type: str
    action_data: Dict[str, Any]
    priority: int = 0
    max_retries: int = 3


class PushNotificationRequest(BaseModel):
    notification_type: str
    title: str
    body: str
    data: Optional[Dict[str, Any]] = None
    push_token: str


class SyncRequest(BaseModel):
    entity_type: str
    sync_token: Optional[str] = None
    data_version: Optional[str] = None


class SyncResponse(BaseModel):
    entity_type: str
    sync_token: str
    data_version: str
    last_sync_at: datetime
    is_syncing: bool
    sync_errors: Optional[Dict[str, Any]] = None


# List Response Models
class MobileAppSessionListResponse(BaseModel):
    sessions: List[MobileAppSessionOut]
    total: int
    page: int
    size: int


class MobileAPICallListResponse(BaseModel):
    calls: List[MobileAPICallOut]
    total: int
    page: int
    size: int


class APICacheListResponse(BaseModel):
    caches: List[APICacheOut]
    total: int
    page: int
    size: int


class MobileAppConfigListResponse(BaseModel):
    configs: List[MobileAppConfigOut]
    total: int
    page: int
    size: int


class MobileFeatureFlagListResponse(BaseModel):
    flags: List[MobileFeatureFlagOut]
    total: int
    page: int
    size: int


class MobilePerformanceMetricListResponse(BaseModel):
    metrics: List[MobilePerformanceMetricOut]
    total: int
    page: int
    size: int


class MobileOfflineQueueListResponse(BaseModel):
    actions: List[MobileOfflineQueueOut]
    total: int
    page: int
    size: int


class MobilePushNotificationListResponse(BaseModel):
    notifications: List[MobilePushNotificationOut]
    total: int
    page: int
    size: int


class MobileSyncStateListResponse(BaseModel):
    sync_states: List[MobileSyncStateOut]
    total: int
    page: int
    size: int


# Analytics and Statistics Models
class MobileAPIAnalytics(BaseModel):
    total_calls: int
    avg_response_time_ms: float
    cache_hit_rate: float
    compression_usage_rate: float
    error_rate: float
    top_endpoints: List[Dict[str, Any]]
    platform_distribution: Dict[str, int]
    network_distribution: Dict[str, int]


class MobilePerformanceSummary(BaseModel):
    avg_app_startup_time: float
    avg_api_response_time: float
    avg_ui_render_time: float
    memory_usage_avg: float
    battery_usage_avg: float
    crash_rate: float
    session_duration_avg: float


class MobileOfflineQueueSummary(BaseModel):
    total_pending: int
    total_processing: int
    total_completed: int
    total_failed: int
    avg_processing_time: float
    top_action_types: List[Dict[str, Any]]
    retry_distribution: Dict[str, int]


class MobilePushNotificationSummary(BaseModel):
    total_sent: int
    total_delivered: int
    total_failed: int
    delivery_rate: float
    avg_delivery_time: float
    top_notification_types: List[Dict[str, Any]]
    platform_distribution: Dict[str, int]


# Utility Models
class MobileAppInfo(BaseModel):
    app_version: str
    platform: str
    device_type: DeviceType
    os_version: Optional[str] = None
    device_model: Optional[str] = None
    screen_resolution: Optional[str] = None
    network_type: Optional[NetworkType] = None


class MobileOptimizationConfig(BaseModel):
    enable_compression: bool = True
    enable_caching: bool = True
    cache_ttl_seconds: int = 300
    max_cache_size_mb: int = 100
    enable_offline_support: bool = True
    max_offline_queue_size: int = 1000
    enable_performance_tracking: bool = True
    enable_push_notifications: bool = True
    enable_feature_flags: bool = True
    enable_sync: bool = True


class MobileHealthCheck(BaseModel):
    session_active: bool
    cache_healthy: bool
    offline_queue_healthy: bool
    push_notifications_healthy: bool
    sync_healthy: bool
    performance_metrics_healthy: bool
    overall_status: str
    last_check: datetime


