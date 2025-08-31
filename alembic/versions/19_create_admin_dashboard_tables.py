"""Create admin dashboard system tables

Revision ID: 19
Revises: 18
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '19'
down_revision = '18'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create admin_role enum
    admin_role_enum = postgresql.ENUM('super_admin', 'admin', 'moderator', 'support', 'analyst', name='admin_role_enum')
    admin_role_enum.create(op.get_bind())
    
    # Create admin_action_type enum
    admin_action_type_enum = postgresql.ENUM('user_management', 'content_moderation', 'payment_management', 'ad_approval', 'system_config', 'security', 'analytics', 'support', name='admin_action_type_enum')
    admin_action_type_enum.create(op.get_bind())
    
    # Create admin_action_status enum
    admin_action_status_enum = postgresql.ENUM('pending', 'approved', 'rejected', 'completed', 'failed', name='admin_action_status_enum')
    admin_action_status_enum.create(op.get_bind())
    
    # Create admin_users table
    op.create_table('admin_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', postgresql.ENUM('super_admin', 'admin', 'moderator', 'support', 'analyst', name='admin_role_enum'), nullable=False),
        sa.Column('permissions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_users_id'), 'admin_users', ['id'], unique=False)
    op.create_index(op.f('ix_admin_users_user_id'), 'admin_users', ['user_id'], unique=True)
    op.create_index(op.f('ix_admin_users_role'), 'admin_users', ['role'], unique=False)
    op.create_index(op.f('ix_admin_users_is_active'), 'admin_users', ['is_active'], unique=False)
    
    # Create admin_actions table
    op.create_table('admin_actions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_user_id', sa.Integer(), nullable=False),
        sa.Column('action_type', postgresql.ENUM('user_management', 'content_moderation', 'payment_management', 'ad_approval', 'system_config', 'security', 'analytics', 'support', name='admin_action_type_enum'), nullable=False),
        sa.Column('action_status', postgresql.ENUM('pending', 'approved', 'rejected', 'completed', 'failed', name='admin_action_status_enum'), nullable=True),
        sa.Column('target_type', sa.String(length=100), nullable=True),
        sa.Column('target_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['admin_user_id'], ['admin_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_actions_id'), 'admin_actions', ['id'], unique=False)
    op.create_index(op.f('ix_admin_actions_admin_user_id'), 'admin_actions', ['admin_user_id'], unique=False)
    op.create_index(op.f('ix_admin_actions_action_type'), 'admin_actions', ['action_type'], unique=False)
    op.create_index(op.f('ix_admin_actions_action_status'), 'admin_actions', ['action_status'], unique=False)
    op.create_index(op.f('ix_admin_actions_created_at'), 'admin_actions', ['created_at'], unique=False)
    
    # Create system_configs table
    op.create_table('system_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('value_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_configs_id'), 'system_configs', ['id'], unique=False)
    op.create_index(op.f('ix_system_configs_key'), 'system_configs', ['key'], unique=True)
    op.create_index(op.f('ix_system_configs_category'), 'system_configs', ['category'], unique=False)
    op.create_index(op.f('ix_system_configs_is_public'), 'system_configs', ['is_public'], unique=False)
    
    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('admin_user_id', sa.Integer(), nullable=True),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('event_category', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('target_type', sa.String(length=100), nullable=True),
        sa.Column('target_id', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['admin_user_id'], ['admin_users.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_admin_user_id'), 'audit_logs', ['admin_user_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_event_type'), 'audit_logs', ['event_type'], unique=False)
    op.create_index(op.f('ix_audit_logs_event_category'), 'audit_logs', ['event_category'], unique=False)
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'], unique=False)
    
    # Create support_tickets table
    op.create_table('support_tickets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('assigned_admin_id', sa.Integer(), nullable=True),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('priority', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['admin_user_id'], ['admin_users.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_support_tickets_id'), 'support_tickets', ['id'], unique=False)
    op.create_index(op.f('ix_support_tickets_user_id'), 'support_tickets', ['user_id'], unique=False)
    op.create_index(op.f('ix_support_tickets_assigned_admin_id'), 'support_tickets', ['assigned_admin_id'], unique=False)
    op.create_index(op.f('ix_support_tickets_status'), 'support_tickets', ['status'], unique=False)
    op.create_index(op.f('ix_support_tickets_priority'), 'support_tickets', ['priority'], unique=False)
    op.create_index(op.f('ix_support_tickets_category'), 'support_tickets', ['category'], unique=False)
    op.create_index(op.f('ix_support_tickets_created_at'), 'support_tickets', ['created_at'], unique=False)
    
    # Create support_messages table
    op.create_table('support_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('admin_user_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_internal', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['admin_user_id'], ['admin_users.id'], ),
        sa.ForeignKeyConstraint(['ticket_id'], ['support_tickets.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_support_messages_id'), 'support_messages', ['id'], unique=False)
    op.create_index(op.f('ix_support_messages_ticket_id'), 'support_messages', ['ticket_id'], unique=False)
    op.create_index(op.f('ix_support_messages_user_id'), 'support_messages', ['user_id'], unique=False)
    op.create_index(op.f('ix_support_messages_admin_user_id'), 'support_messages', ['admin_user_id'], unique=False)
    op.create_index(op.f('ix_support_messages_created_at'), 'support_messages', ['created_at'], unique=False)
    
    # Create content_moderation table
    op.create_table('content_moderation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=False),
        sa.Column('reported_by', sa.Integer(), nullable=True),
        sa.Column('assigned_admin_id', sa.Integer(), nullable=True),
        sa.Column('reason', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('action_taken', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['admin_user_id'], ['admin_users.id'], ),
        sa.ForeignKeyConstraint(['reported_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_content_moderation_id'), 'content_moderation', ['id'], unique=False)
    op.create_index(op.f('ix_content_moderation_content_type'), 'content_moderation', ['content_type'], unique=False)
    op.create_index(op.f('ix_content_moderation_content_id'), 'content_moderation', ['content_id'], unique=False)
    op.create_index(op.f('ix_content_moderation_reported_by'), 'content_moderation', ['reported_by'], unique=False)
    op.create_index(op.f('ix_content_moderation_assigned_admin_id'), 'content_moderation', ['assigned_admin_id'], unique=False)
    op.create_index(op.f('ix_content_moderation_status'), 'content_moderation', ['status'], unique=False)
    op.create_index(op.f('ix_content_moderation_created_at'), 'content_moderation', ['created_at'], unique=False)
    
    # Create system_metrics table
    op.create_table('system_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('metric_name', sa.String(length=255), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('metric_unit', sa.String(length=50), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_metrics_id'), 'system_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_system_metrics_metric_name'), 'system_metrics', ['metric_name'], unique=False)
    op.create_index(op.f('ix_system_metrics_category'), 'system_metrics', ['category'], unique=False)
    op.create_index(op.f('ix_system_metrics_timestamp'), 'system_metrics', ['timestamp'], unique=False)
    
    # Create admin_dashboards table
    op.create_table('admin_dashboards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('layout', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('widgets', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('filters', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['admin_user_id'], ['admin_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_dashboards_id'), 'admin_dashboards', ['id'], unique=False)
    op.create_index(op.f('ix_admin_dashboards_admin_user_id'), 'admin_dashboards', ['admin_user_id'], unique=False)
    op.create_index(op.f('ix_admin_dashboards_name'), 'admin_dashboards', ['name'], unique=False)
    op.create_index(op.f('ix_admin_dashboards_is_default'), 'admin_dashboards', ['is_default'], unique=False)
    op.create_index(op.f('ix_admin_dashboards_is_public'), 'admin_dashboards', ['is_public'], unique=False)
    
    # Create admin_notifications table
    op.create_table('admin_notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('notification_type', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('action_url', sa.String(length=500), nullable=True),
        sa.Column('action_text', sa.String(length=100), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('is_urgent', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['admin_user_id'], ['admin_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_notifications_id'), 'admin_notifications', ['id'], unique=False)
    op.create_index(op.f('ix_admin_notifications_admin_user_id'), 'admin_notifications', ['admin_user_id'], unique=False)
    op.create_index(op.f('ix_admin_notifications_notification_type'), 'admin_notifications', ['notification_type'], unique=False)
    op.create_index(op.f('ix_admin_notifications_category'), 'admin_notifications', ['category'], unique=False)
    op.create_index(op.f('ix_admin_notifications_is_read'), 'admin_notifications', ['is_read'], unique=False)
    op.create_index(op.f('ix_admin_notifications_is_urgent'), 'admin_notifications', ['is_urgent'], unique=False)
    op.create_index(op.f('ix_admin_notifications_created_at'), 'admin_notifications', ['created_at'], unique=False)
    
    # Create ip_blocklist table
    op.create_table('ip_blocklist',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('block_type', sa.String(length=50), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('added_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['added_by'], ['admin_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ip_blocklist_id'), 'ip_blocklist', ['id'], unique=False)
    op.create_index(op.f('ix_ip_blocklist_ip_address'), 'ip_blocklist', ['ip_address'], unique=True)
    op.create_index(op.f('ix_ip_blocklist_block_type'), 'ip_blocklist', ['block_type'], unique=False)
    op.create_index(op.f('ix_ip_blocklist_added_by'), 'ip_blocklist', ['added_by'], unique=False)
    op.create_index(op.f('ix_ip_blocklist_expires_at'), 'ip_blocklist', ['expires_at'], unique=False)
    
    # Create admin_reports table
    op.create_table('admin_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_name', sa.String(length=255), nullable=False),
        sa.Column('report_type', sa.String(length=100), nullable=False),
        sa.Column('generated_by', sa.Integer(), nullable=False),
        sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['generated_by'], ['admin_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_reports_id'), 'admin_reports', ['id'], unique=False)
    op.create_index(op.f('ix_admin_reports_report_name'), 'admin_reports', ['report_name'], unique=False)
    op.create_index(op.f('ix_admin_reports_report_type'), 'admin_reports', ['report_type'], unique=False)
    op.create_index(op.f('ix_admin_reports_generated_by'), 'admin_reports', ['generated_by'], unique=False)
    op.create_index(op.f('ix_admin_reports_status'), 'admin_reports', ['status'], unique=False)
    op.create_index(op.f('ix_admin_reports_created_at'), 'admin_reports', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_admin_reports_created_at'), table_name='admin_reports')
    op.drop_index(op.f('ix_admin_reports_status'), table_name='admin_reports')
    op.drop_index(op.f('ix_admin_reports_generated_by'), table_name='admin_reports')
    op.drop_index(op.f('ix_admin_reports_report_type'), table_name='admin_reports')
    op.drop_index(op.f('ix_admin_reports_report_name'), table_name='admin_reports')
    op.drop_index(op.f('ix_admin_reports_id'), table_name='admin_reports')
    
    op.drop_index(op.f('ix_ip_blocklist_expires_at'), table_name='ip_blocklist')
    op.drop_index(op.f('ix_ip_blocklist_added_by'), table_name='ip_blocklist')
    op.drop_index(op.f('ix_ip_blocklist_block_type'), table_name='ip_blocklist')
    op.drop_index(op.f('ix_ip_blocklist_ip_address'), table_name='ip_blocklist')
    op.drop_index(op.f('ix_ip_blocklist_id'), table_name='ip_blocklist')
    
    op.drop_index(op.f('ix_admin_notifications_created_at'), table_name='admin_notifications')
    op.drop_index(op.f('ix_admin_notifications_is_urgent'), table_name='admin_notifications')
    op.drop_index(op.f('ix_admin_notifications_is_read'), table_name='admin_notifications')
    op.drop_index(op.f('ix_admin_notifications_category'), table_name='admin_notifications')
    op.drop_index(op.f('ix_admin_notifications_notification_type'), table_name='admin_notifications')
    op.drop_index(op.f('ix_admin_notifications_admin_user_id'), table_name='admin_notifications')
    op.drop_index(op.f('ix_admin_notifications_id'), table_name='admin_notifications')
    
    op.drop_index(op.f('ix_admin_dashboards_is_public'), table_name='admin_dashboards')
    op.drop_index(op.f('ix_admin_dashboards_is_default'), table_name='admin_dashboards')
    op.drop_index(op.f('ix_admin_dashboards_name'), table_name='admin_dashboards')
    op.drop_index(op.f('ix_admin_dashboards_admin_user_id'), table_name='admin_dashboards')
    op.drop_index(op.f('ix_admin_dashboards_id'), table_name='admin_dashboards')
    
    op.drop_index(op.f('ix_system_metrics_timestamp'), table_name='system_metrics')
    op.drop_index(op.f('ix_system_metrics_category'), table_name='system_metrics')
    op.drop_index(op.f('ix_system_metrics_metric_name'), table_name='system_metrics')
    op.drop_index(op.f('ix_system_metrics_id'), table_name='system_metrics')
    
    op.drop_index(op.f('ix_content_moderation_created_at'), table_name='content_moderation')
    op.drop_index(op.f('ix_content_moderation_status'), table_name='content_moderation')
    op.drop_index(op.f('ix_content_moderation_assigned_admin_id'), table_name='content_moderation')
    op.drop_index(op.f('ix_content_moderation_reported_by'), table_name='content_moderation')
    op.drop_index(op.f('ix_content_moderation_content_id'), table_name='content_moderation')
    op.drop_index(op.f('ix_content_moderation_content_type'), table_name='content_moderation')
    op.drop_index(op.f('ix_content_moderation_id'), table_name='content_moderation')
    
    op.drop_index(op.f('ix_support_messages_created_at'), table_name='support_messages')
    op.drop_index(op.f('ix_support_messages_admin_user_id'), table_name='support_messages')
    op.drop_index(op.f('ix_support_messages_user_id'), table_name='support_messages')
    op.drop_index(op.f('ix_support_messages_ticket_id'), table_name='support_messages')
    op.drop_index(op.f('ix_support_messages_id'), table_name='support_messages')
    
    op.drop_index(op.f('ix_support_tickets_created_at'), table_name='support_tickets')
    op.drop_index(op.f('ix_support_tickets_category'), table_name='support_tickets')
    op.drop_index(op.f('ix_support_tickets_priority'), table_name='support_tickets')
    op.drop_index(op.f('ix_support_tickets_status'), table_name='support_tickets')
    op.drop_index(op.f('ix_support_tickets_assigned_admin_id'), table_name='support_tickets')
    op.drop_index(op.f('ix_support_tickets_user_id'), table_name='support_tickets')
    op.drop_index(op.f('ix_support_tickets_id'), table_name='support_tickets')
    
    op.drop_index(op.f('ix_audit_logs_created_at'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_event_category'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_event_type'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_admin_user_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_id'), table_name='audit_logs')
    
    op.drop_index(op.f('ix_system_configs_is_public'), table_name='system_configs')
    op.drop_index(op.f('ix_system_configs_category'), table_name='system_configs')
    op.drop_index(op.f('ix_system_configs_key'), table_name='system_configs')
    op.drop_index(op.f('ix_system_configs_id'), table_name='system_configs')
    
    op.drop_index(op.f('ix_admin_actions_created_at'), table_name='admin_actions')
    op.drop_index(op.f('ix_admin_actions_action_status'), table_name='admin_actions')
    op.drop_index(op.f('ix_admin_actions_action_type'), table_name='admin_actions')
    op.drop_index(op.f('ix_admin_actions_admin_user_id'), table_name='admin_actions')
    op.drop_index(op.f('ix_admin_actions_id'), table_name='admin_actions')
    
    op.drop_index(op.f('ix_admin_users_is_active'), table_name='admin_users')
    op.drop_index(op.f('ix_admin_users_role'), table_name='admin_users')
    op.drop_index(op.f('ix_admin_users_user_id'), table_name='admin_users')
    op.drop_index(op.f('ix_admin_users_id'), table_name='admin_users')
    
    # Drop tables
    op.drop_table('admin_reports')
    op.drop_table('ip_blocklist')
    op.drop_table('admin_notifications')
    op.drop_table('admin_dashboards')
    op.drop_table('system_metrics')
    op.drop_table('content_moderation')
    op.drop_table('support_messages')
    op.drop_table('support_tickets')
    op.drop_table('audit_logs')
    op.drop_table('system_configs')
    op.drop_table('admin_actions')
    op.drop_table('admin_users')
    
    # Drop enums
    admin_action_status_enum = postgresql.ENUM('pending', 'approved', 'rejected', 'completed', 'failed', name='admin_action_status_enum')
    admin_action_status_enum.drop(op.get_bind())
    
    admin_action_type_enum = postgresql.ENUM('user_management', 'content_moderation', 'payment_management', 'ad_approval', 'system_config', 'security', 'analytics', 'support', name='admin_action_type_enum')
    admin_action_type_enum.drop(op.get_bind())
    
    admin_role_enum = postgresql.ENUM('super_admin', 'admin', 'moderator', 'support', 'analyst', name='admin_role_enum')
    admin_role_enum.drop(op.get_bind())


