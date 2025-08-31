"""Create mobile API optimization tables

Revision ID: 23
Revises: 22
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '23'
down_revision = '22'
branch_labels = None
depends_on = None


def upgrade():
    # Create mobile_app_sessions table
    op.create_table('mobile_app_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('device_id', sa.String(length=255), nullable=False),
        sa.Column('device_type', sa.String(length=50), nullable=False),
        sa.Column('app_version', sa.String(length=50), nullable=True),
        sa.Column('os_version', sa.String(length=50), nullable=True),
        sa.Column('device_model', sa.String(length=100), nullable=True),
        sa.Column('screen_resolution', sa.String(length=50), nullable=True),
        sa.Column('network_type', sa.String(length=50), nullable=True),
        sa.Column('location_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('push_token', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_activity', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mobile_app_sessions_id'), 'mobile_app_sessions', ['id'], unique=False)
    op.create_index('idx_mobile_sessions_session_id', 'mobile_app_sessions', ['session_id'], unique=True)
    op.create_index('idx_mobile_sessions_user_device', 'mobile_app_sessions', ['user_id', 'device_id'], unique=False)
    op.create_index('idx_mobile_sessions_active', 'mobile_app_sessions', ['is_active', 'last_activity'], unique=False)
    
    # Create mobile_api_calls table
    op.create_table('mobile_api_calls',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('endpoint', sa.String(length=255), nullable=False),
        sa.Column('method', sa.String(length=10), nullable=False),
        sa.Column('request_size', sa.Integer(), nullable=True),
        sa.Column('response_size', sa.Integer(), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('cache_hit', sa.Boolean(), nullable=True),
        sa.Column('compression_used', sa.Boolean(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['mobile_app_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mobile_api_calls_id'), 'mobile_api_calls', ['id'], unique=False)
    op.create_index('idx_api_calls_session_endpoint', 'mobile_api_calls', ['session_id', 'endpoint'], unique=False)
    op.create_index('idx_api_calls_response_time', 'mobile_api_calls', ['response_time_ms'], unique=False)
    
    # Create api_cache table
    op.create_table('api_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cache_key', sa.String(length=255), nullable=False),
        sa.Column('endpoint', sa.String(length=255), nullable=False),
        sa.Column('method', sa.String(length=10), nullable=False),
        sa.Column('request_hash', sa.String(length=64), nullable=False),
        sa.Column('response_data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('response_headers', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('content_type', sa.String(length=100), nullable=True),
        sa.Column('compression_type', sa.String(length=20), nullable=True),
        sa.Column('cache_control', sa.String(length=100), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('hit_count', sa.Integer(), nullable=True),
        sa.Column('last_accessed', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_api_cache_id'), 'api_cache', ['id'], unique=False)
    op.create_index('idx_api_cache_key', 'api_cache', ['cache_key'], unique=True)
    op.create_index('idx_api_cache_endpoint_expires', 'api_cache', ['endpoint', 'expires_at'], unique=False)
    op.create_index('idx_api_cache_key_expires', 'api_cache', ['cache_key', 'expires_at'], unique=False)
    
    # Create mobile_app_configs table
    op.create_table('mobile_app_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('app_version', sa.String(length=50), nullable=False),
        sa.Column('platform', sa.String(length=20), nullable=False),
        sa.Column('config_data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('min_version_required', sa.String(length=50), nullable=True),
        sa.Column('force_update', sa.Boolean(), nullable=True),
        sa.Column('maintenance_mode', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mobile_app_configs_id'), 'mobile_app_configs', ['id'], unique=False)
    op.create_index('idx_mobile_config_platform_version', 'mobile_app_configs', ['platform', 'app_version'], unique=False)
    
    # Create mobile_feature_flags table
    op.create_table('mobile_feature_flags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('feature_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=True),
        sa.Column('rollout_percentage', sa.Float(), nullable=True),
        sa.Column('target_platforms', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('min_app_version', sa.String(length=50), nullable=True),
        sa.Column('max_app_version', sa.String(length=50), nullable=True),
        sa.Column('user_segments', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mobile_feature_flags_id'), 'mobile_feature_flags', ['id'], unique=False)
    op.create_index('idx_feature_flags_name', 'mobile_feature_flags', ['feature_name'], unique=True)
    op.create_index('idx_feature_flags_enabled', 'mobile_feature_flags', ['is_enabled', 'feature_name'], unique=False)
    
    # Create mobile_performance_metrics table
    op.create_table('mobile_performance_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('metric_type', sa.String(length=50), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('metric_unit', sa.String(length=20), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['mobile_app_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mobile_performance_metrics_id'), 'mobile_performance_metrics', ['id'], unique=False)
    op.create_index('idx_performance_metrics_session_type', 'mobile_performance_metrics', ['session_id', 'metric_type'], unique=False)
    
    # Create mobile_offline_queue table
    op.create_table('mobile_offline_queue',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('action_type', sa.String(length=50), nullable=False),
        sa.Column('action_data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True),
        sa.Column('max_retries', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['mobile_app_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mobile_offline_queue_id'), 'mobile_offline_queue', ['id'], unique=False)
    op.create_index('idx_offline_queue_session_status', 'mobile_offline_queue', ['session_id', 'status'], unique=False)
    
    # Create mobile_push_notifications table
    op.create_table('mobile_push_notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('notification_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('push_token', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['mobile_app_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mobile_push_notifications_id'), 'mobile_push_notifications', ['id'], unique=False)
    op.create_index('idx_push_notifications_session_status', 'mobile_push_notifications', ['session_id', 'status'], unique=False)
    
    # Create mobile_sync_states table
    op.create_table('mobile_sync_states',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sync_token', sa.String(length=255), nullable=True),
        sa.Column('data_version', sa.String(length=50), nullable=True),
        sa.Column('is_syncing', sa.Boolean(), nullable=True),
        sa.Column('sync_errors', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['mobile_app_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mobile_sync_states_id'), 'mobile_sync_states', ['id'], unique=False)
    op.create_index('idx_sync_states_session_entity', 'mobile_sync_states', ['session_id', 'entity_type'], unique=False)


def downgrade():
    # Drop tables
    op.drop_index('idx_sync_states_session_entity', table_name='mobile_sync_states')
    op.drop_index(op.f('ix_mobile_sync_states_id'), table_name='mobile_sync_states')
    op.drop_table('mobile_sync_states')
    
    op.drop_index('idx_push_notifications_session_status', table_name='mobile_push_notifications')
    op.drop_index(op.f('ix_mobile_push_notifications_id'), table_name='mobile_push_notifications')
    op.drop_table('mobile_push_notifications')
    
    op.drop_index('idx_offline_queue_session_status', table_name='mobile_offline_queue')
    op.drop_index(op.f('ix_mobile_offline_queue_id'), table_name='mobile_offline_queue')
    op.drop_table('mobile_offline_queue')
    
    op.drop_index('idx_performance_metrics_session_type', table_name='mobile_performance_metrics')
    op.drop_index(op.f('ix_mobile_performance_metrics_id'), table_name='mobile_performance_metrics')
    op.drop_table('mobile_performance_metrics')
    
    op.drop_index('idx_feature_flags_enabled', table_name='mobile_feature_flags')
    op.drop_index('idx_feature_flags_name', table_name='mobile_feature_flags')
    op.drop_index(op.f('ix_mobile_feature_flags_id'), table_name='mobile_feature_flags')
    op.drop_table('mobile_feature_flags')
    
    op.drop_index('idx_mobile_config_platform_version', table_name='mobile_app_configs')
    op.drop_index(op.f('ix_mobile_app_configs_id'), table_name='mobile_app_configs')
    op.drop_table('mobile_app_configs')
    
    op.drop_index('idx_api_cache_key_expires', table_name='api_cache')
    op.drop_index('idx_api_cache_endpoint_expires', table_name='api_cache')
    op.drop_index('idx_api_cache_key', table_name='api_cache')
    op.drop_index(op.f('ix_api_cache_id'), table_name='api_cache')
    op.drop_table('api_cache')
    
    op.drop_index('idx_api_calls_response_time', table_name='mobile_api_calls')
    op.drop_index('idx_api_calls_session_endpoint', table_name='mobile_api_calls')
    op.drop_index(op.f('ix_mobile_api_calls_id'), table_name='mobile_api_calls')
    op.drop_table('mobile_api_calls')
    
    op.drop_index('idx_mobile_sessions_active', table_name='mobile_app_sessions')
    op.drop_index('idx_mobile_sessions_user_device', table_name='mobile_app_sessions')
    op.drop_index('idx_mobile_sessions_session_id', table_name='mobile_app_sessions')
    op.drop_index(op.f('ix_mobile_app_sessions_id'), table_name='mobile_app_sessions')
    op.drop_table('mobile_app_sessions')


