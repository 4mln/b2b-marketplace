"""Create analytics and reporting system tables

Revision ID: 22
Revises: 21
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '22'
down_revision = '21'
branch_labels = None
depends_on = None


def upgrade():
    # Create analytics_events table
    op.create_table('analytics_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('event_name', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('entity_type', sa.String(length=50), nullable=True),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('event_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analytics_events_id'), 'analytics_events', ['id'], unique=False)
    op.create_index('idx_analytics_events_type', 'analytics_events', ['event_type'], unique=False)
    op.create_index('idx_analytics_events_user', 'analytics_events', ['user_id'], unique=False)
    op.create_index('idx_analytics_events_entity', 'analytics_events', ['entity_type', 'entity_id'], unique=False)
    op.create_index('idx_analytics_events_created', 'analytics_events', ['created_at'], unique=False)
    
    # Create business_metrics table
    op.create_table('business_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('total_users', sa.Integer(), nullable=True),
        sa.Column('new_users', sa.Integer(), nullable=True),
        sa.Column('active_users', sa.Integer(), nullable=True),
        sa.Column('total_sellers', sa.Integer(), nullable=True),
        sa.Column('new_sellers', sa.Integer(), nullable=True),
        sa.Column('total_products', sa.Integer(), nullable=True),
        sa.Column('new_products', sa.Integer(), nullable=True),
        sa.Column('total_orders', sa.Integer(), nullable=True),
        sa.Column('order_value', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('avg_order_value', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('total_revenue', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_business_metrics_id'), 'business_metrics', ['id'], unique=False)
    op.create_index('idx_business_metrics_date', 'business_metrics', ['date'], unique=False)
    
    # Create user_analytics table
    op.create_table('user_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('login_count', sa.Integer(), nullable=True),
        sa.Column('session_duration', sa.Integer(), nullable=True),
        sa.Column('page_views', sa.Integer(), nullable=True),
        sa.Column('searches', sa.Integer(), nullable=True),
        sa.Column('orders_placed', sa.Integer(), nullable=True),
        sa.Column('total_spent', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_analytics_id'), 'user_analytics', ['id'], unique=False)
    op.create_index('idx_user_analytics_user_date', 'user_analytics', ['user_id', 'date'], unique=False)
    
    # Create seller_analytics table
    op.create_table('seller_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('seller_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('products_listed', sa.Integer(), nullable=True),
        sa.Column('products_sold', sa.Integer(), nullable=True),
        sa.Column('total_revenue', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('total_orders', sa.Integer(), nullable=True),
        sa.Column('avg_order_value', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('store_views', sa.Integer(), nullable=True),
        sa.Column('product_views', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['seller_id'], ['sellers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_seller_analytics_id'), 'seller_analytics', ['id'], unique=False)
    op.create_index('idx_seller_analytics_seller_date', 'seller_analytics', ['seller_id', 'date'], unique=False)
    
    # Create product_analytics table
    op.create_table('product_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('views', sa.Integer(), nullable=True),
        sa.Column('clicks', sa.Integer(), nullable=True),
        sa.Column('orders', sa.Integer(), nullable=True),
        sa.Column('revenue', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('conversion_rate', sa.Float(), nullable=True),
        sa.Column('avg_rating', sa.Float(), nullable=True),
        sa.Column('review_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_analytics_id'), 'product_analytics', ['id'], unique=False)
    op.create_index('idx_product_analytics_product_date', 'product_analytics', ['product_id', 'date'], unique=False)
    
    # Create financial_reports table
    op.create_table('financial_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_type', sa.String(length=50), nullable=False),
        sa.Column('report_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('total_revenue', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('total_orders', sa.Integer(), nullable=True),
        sa.Column('avg_order_value', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('commission_revenue', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('payment_processing_fees', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('net_revenue', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('report_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_financial_reports_id'), 'financial_reports', ['id'], unique=False)
    op.create_index('idx_financial_reports_type_date', 'financial_reports', ['report_type', 'report_date'], unique=False)
    
    # Create performance_metrics table
    op.create_table('performance_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('metric_type', sa.String(length=50), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('metric_unit', sa.String(length=20), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_performance_metrics_id'), 'performance_metrics', ['id'], unique=False)
    op.create_index('idx_performance_metrics_type_name', 'performance_metrics', ['metric_type', 'metric_name'], unique=False)
    op.create_index('idx_performance_metrics_timestamp', 'performance_metrics', ['timestamp'], unique=False)
    
    # Create report_templates table
    op.create_table('report_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('report_type', sa.String(length=50), nullable=False),
        sa.Column('template_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_report_templates_id'), 'report_templates', ['id'], unique=False)
    op.create_index('idx_report_templates_type', 'report_templates', ['report_type'], unique=False)
    op.create_index('idx_report_templates_active', 'report_templates', ['is_active'], unique=False)
    
    # Create scheduled_reports table
    op.create_table('scheduled_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.Column('schedule_type', sa.String(length=20), nullable=False),
        sa.Column('schedule_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('recipients', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['template_id'], ['report_templates.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scheduled_reports_id'), 'scheduled_reports', ['id'], unique=False)
    op.create_index('idx_scheduled_reports_active', 'scheduled_reports', ['is_active'], unique=False)
    op.create_index('idx_scheduled_reports_next_run', 'scheduled_reports', ['next_run_at'], unique=False)
    
    # Create report_executions table
    op.create_table('report_executions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_name', sa.String(length=255), nullable=False),
        sa.Column('execution_type', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('result_file_path', sa.String(length=500), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_report_executions_id'), 'report_executions', ['id'], unique=False)
    op.create_index('idx_report_executions_status', 'report_executions', ['status'], unique=False)
    op.create_index('idx_report_executions_created', 'report_executions', ['created_at'], unique=False)
    
    # Create dashboards table
    op.create_table('dashboards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('layout_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('widgets', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dashboards_id'), 'dashboards', ['id'], unique=False)
    op.create_index('idx_dashboards_user', 'dashboards', ['user_id'], unique=False)
    op.create_index('idx_dashboards_default', 'dashboards', ['user_id', 'is_default'], unique=False)
    
    # Create data_exports table
    op.create_table('data_exports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('export_type', sa.String(length=50), nullable=False),
        sa.Column('export_format', sa.String(length=20), nullable=False),
        sa.Column('filters', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('download_count', sa.Integer(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_data_exports_id'), 'data_exports', ['id'], unique=False)
    op.create_index('idx_data_exports_user', 'data_exports', ['user_id'], unique=False)
    op.create_index('idx_data_exports_status', 'data_exports', ['status'], unique=False)
    op.create_index('idx_data_exports_expires', 'data_exports', ['expires_at'], unique=False)


def downgrade():
    # Drop tables
    op.drop_index('idx_data_exports_expires', table_name='data_exports')
    op.drop_index('idx_data_exports_status', table_name='data_exports')
    op.drop_index('idx_data_exports_user', table_name='data_exports')
    op.drop_index(op.f('ix_data_exports_id'), table_name='data_exports')
    op.drop_table('data_exports')
    
    op.drop_index('idx_dashboards_default', table_name='dashboards')
    op.drop_index('idx_dashboards_user', table_name='dashboards')
    op.drop_index(op.f('ix_dashboards_id'), table_name='dashboards')
    op.drop_table('dashboards')
    
    op.drop_index('idx_report_executions_created', table_name='report_executions')
    op.drop_index('idx_report_executions_status', table_name='report_executions')
    op.drop_index(op.f('ix_report_executions_id'), table_name='report_executions')
    op.drop_table('report_executions')
    
    op.drop_index('idx_scheduled_reports_next_run', table_name='scheduled_reports')
    op.drop_index('idx_scheduled_reports_active', table_name='scheduled_reports')
    op.drop_index(op.f('ix_scheduled_reports_id'), table_name='scheduled_reports')
    op.drop_table('scheduled_reports')
    
    op.drop_index('idx_report_templates_active', table_name='report_templates')
    op.drop_index('idx_report_templates_type', table_name='report_templates')
    op.drop_index(op.f('ix_report_templates_id'), table_name='report_templates')
    op.drop_table('report_templates')
    
    op.drop_index('idx_performance_metrics_timestamp', table_name='performance_metrics')
    op.drop_index('idx_performance_metrics_type_name', table_name='performance_metrics')
    op.drop_index(op.f('ix_performance_metrics_id'), table_name='performance_metrics')
    op.drop_table('performance_metrics')
    
    op.drop_index('idx_financial_reports_type_date', table_name='financial_reports')
    op.drop_index(op.f('ix_financial_reports_id'), table_name='financial_reports')
    op.drop_table('financial_reports')
    
    op.drop_index('idx_product_analytics_product_date', table_name='product_analytics')
    op.drop_index(op.f('ix_product_analytics_id'), table_name='product_analytics')
    op.drop_table('product_analytics')
    
    op.drop_index('idx_seller_analytics_seller_date', table_name='seller_analytics')
    op.drop_index(op.f('ix_seller_analytics_id'), table_name='seller_analytics')
    op.drop_table('seller_analytics')
    
    op.drop_index('idx_user_analytics_user_date', table_name='user_analytics')
    op.drop_index(op.f('ix_user_analytics_id'), table_name='user_analytics')
    op.drop_table('user_analytics')
    
    op.drop_index('idx_business_metrics_date', table_name='business_metrics')
    op.drop_index(op.f('ix_business_metrics_id'), table_name='business_metrics')
    op.drop_table('business_metrics')
    
    op.drop_index('idx_analytics_events_created', table_name='analytics_events')
    op.drop_index('idx_analytics_events_entity', table_name='analytics_events')
    op.drop_index('idx_analytics_events_user', table_name='analytics_events')
    op.drop_index('idx_analytics_events_type', table_name='analytics_events')
    op.drop_index(op.f('ix_analytics_events_id'), table_name='analytics_events')
    op.drop_table('analytics_events')
