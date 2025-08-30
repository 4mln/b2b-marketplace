"""Create notification system tables

Revision ID: 21
Revises: 20
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '21'
down_revision = '20'
branch_labels = None
depends_on = None


def upgrade():
    # Create notifications table
    op.create_table('notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('summary', sa.String(length=500), nullable=True),
        sa.Column('data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('action_url', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('channels', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('sent_channels', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('source_type', sa.String(length=50), nullable=True),
        sa.Column('source_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)
    op.create_index('idx_notifications_user_status', 'notifications', ['user_id', 'status'], unique=False)
    op.create_index('idx_notifications_type_status', 'notifications', ['type', 'status'], unique=False)
    op.create_index('idx_notifications_scheduled', 'notifications', ['scheduled_at'], unique=False)
    op.create_index('idx_notifications_created', 'notifications', ['created_at'], unique=False)
    
    # Create notification_delivery_attempts table
    op.create_table('notification_delivery_attempts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('notification_id', sa.Integer(), nullable=False),
        sa.Column('channel', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True),
        sa.Column('next_retry_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['notification_id'], ['notifications.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_delivery_attempts_id'), 'notification_delivery_attempts', ['id'], unique=False)
    op.create_index('idx_delivery_attempts_notification', 'notification_delivery_attempts', ['notification_id'], unique=False)
    op.create_index('idx_delivery_attempts_channel_status', 'notification_delivery_attempts', ['channel', 'status'], unique=False)
    op.create_index('idx_delivery_attempts_sent', 'notification_delivery_attempts', ['sent_at'], unique=False)
    
    # Create notification_templates table
    op.create_table('notification_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('title_template', sa.String(length=255), nullable=False),
        sa.Column('message_template', sa.Text(), nullable=False),
        sa.Column('summary_template', sa.String(length=500), nullable=True),
        sa.Column('email_subject', sa.String(length=255), nullable=True),
        sa.Column('email_body', sa.Text(), nullable=True),
        sa.Column('sms_template', sa.String(length=160), nullable=True),
        sa.Column('push_title', sa.String(length=100), nullable=True),
        sa.Column('push_body', sa.String(length=200), nullable=True),
        sa.Column('channels', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('variables', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_templates_id'), 'notification_templates', ['id'], unique=False)
    op.create_index('idx_templates_type_language', 'notification_templates', ['type', 'language'], unique=False)
    op.create_index('idx_templates_active', 'notification_templates', ['is_active'], unique=False)
    
    # Create user_notification_preferences table
    op.create_table('user_notification_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('notification_type', sa.String(length=50), nullable=False),
        sa.Column('in_app_enabled', sa.Boolean(), nullable=True),
        sa.Column('email_enabled', sa.Boolean(), nullable=True),
        sa.Column('sms_enabled', sa.Boolean(), nullable=True),
        sa.Column('push_enabled', sa.Boolean(), nullable=True),
        sa.Column('quiet_hours_start', sa.String(length=5), nullable=True),
        sa.Column('quiet_hours_end', sa.String(length=5), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=True),
        sa.Column('frequency', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_notification_preferences_id'), 'user_notification_preferences', ['id'], unique=False)
    op.create_index('idx_user_preferences_user_type', 'user_notification_preferences', ['user_id', 'notification_type'], unique=False)
    op.create_index('idx_user_preferences_enabled', 'user_notification_preferences', ['in_app_enabled', 'email_enabled'], unique=False)
    
    # Create notification_subscriptions table
    op.create_table('notification_subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('topic', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=True),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('channels', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_subscriptions_id'), 'notification_subscriptions', ['id'], unique=False)
    op.create_index('idx_subscriptions_user_topic', 'notification_subscriptions', ['user_id', 'topic'], unique=False)
    op.create_index('idx_subscriptions_active', 'notification_subscriptions', ['is_active'], unique=False)
    
    # Create notification_batches table
    op.create_table('notification_batches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('target_type', sa.String(length=50), nullable=False),
        sa.Column('target_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('channels', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('total_recipients', sa.Integer(), nullable=True),
        sa.Column('sent_count', sa.Integer(), nullable=True),
        sa.Column('failed_count', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['template_id'], ['notification_templates.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_batches_id'), 'notification_batches', ['id'], unique=False)
    op.create_index('idx_batches_status', 'notification_batches', ['status'], unique=False)
    op.create_index('idx_batches_scheduled', 'notification_batches', ['scheduled_at'], unique=False)
    
    # Create notification_webhooks table
    op.create_table('notification_webhooks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('notification_types', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('headers', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('secret_key', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_triggered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('success_count', sa.Integer(), nullable=True),
        sa.Column('failure_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_webhooks_id'), 'notification_webhooks', ['id'], unique=False)
    
    # Create notification_analytics table
    op.create_table('notification_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('total_sent', sa.Integer(), nullable=True),
        sa.Column('total_delivered', sa.Integer(), nullable=True),
        sa.Column('total_read', sa.Integer(), nullable=True),
        sa.Column('total_failed', sa.Integer(), nullable=True),
        sa.Column('in_app_sent', sa.Integer(), nullable=True),
        sa.Column('email_sent', sa.Integer(), nullable=True),
        sa.Column('sms_sent', sa.Integer(), nullable=True),
        sa.Column('push_sent', sa.Integer(), nullable=True),
        sa.Column('notifications_by_type', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('avg_delivery_time_ms', sa.Integer(), nullable=True),
        sa.Column('avg_read_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_analytics_id'), 'notification_analytics', ['id'], unique=False)
    op.create_index('idx_analytics_date', 'notification_analytics', ['date'], unique=False)


def downgrade():
    # Drop tables
    op.drop_index('idx_analytics_date', table_name='notification_analytics')
    op.drop_index(op.f('ix_notification_analytics_id'), table_name='notification_analytics')
    op.drop_table('notification_analytics')
    
    op.drop_index(op.f('ix_notification_webhooks_id'), table_name='notification_webhooks')
    op.drop_table('notification_webhooks')
    
    op.drop_index('idx_batches_scheduled', table_name='notification_batches')
    op.drop_index('idx_batches_status', table_name='notification_batches')
    op.drop_index(op.f('ix_notification_batches_id'), table_name='notification_batches')
    op.drop_table('notification_batches')
    
    op.drop_index('idx_subscriptions_active', table_name='notification_subscriptions')
    op.drop_index('idx_subscriptions_user_topic', table_name='notification_subscriptions')
    op.drop_index(op.f('ix_notification_subscriptions_id'), table_name='notification_subscriptions')
    op.drop_table('notification_subscriptions')
    
    op.drop_index('idx_user_preferences_enabled', table_name='user_notification_preferences')
    op.drop_index('idx_user_preferences_user_type', table_name='user_notification_preferences')
    op.drop_index(op.f('ix_user_notification_preferences_id'), table_name='user_notification_preferences')
    op.drop_table('user_notification_preferences')
    
    op.drop_index('idx_templates_active', table_name='notification_templates')
    op.drop_index('idx_templates_type_language', table_name='notification_templates')
    op.drop_index(op.f('ix_notification_templates_id'), table_name='notification_templates')
    op.drop_table('notification_templates')
    
    op.drop_index('idx_delivery_attempts_sent', table_name='notification_delivery_attempts')
    op.drop_index('idx_delivery_attempts_channel_status', table_name='notification_delivery_attempts')
    op.drop_index('idx_delivery_attempts_notification', table_name='notification_delivery_attempts')
    op.drop_index(op.f('ix_notification_delivery_attempts_id'), table_name='notification_delivery_attempts')
    op.drop_table('notification_delivery_attempts')
    
    op.drop_index('idx_notifications_created', table_name='notifications')
    op.drop_index('idx_notifications_scheduled', table_name='notifications')
    op.drop_index('idx_notifications_type_status', table_name='notifications')
    op.drop_index('idx_notifications_user_status', table_name='notifications')
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    op.drop_table('notifications')
