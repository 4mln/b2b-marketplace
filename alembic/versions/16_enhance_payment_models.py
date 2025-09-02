"""enhance payment models with Iran payment providers

Revision ID: 16_enhance_payment_models
Revises: 15_enhance_seller_model
Create Date: 2025-08-29 04:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '16_enhance_payment_models'
down_revision = '15_enhance_seller_model'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop existing payments table if it exists
    op.drop_table('payments', if_exists=True)
    
    # Create enhanced payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(), nullable=False, server_default='IRR'),
        sa.Column('payment_method', sa.String(), nullable=False),
        sa.Column('payment_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('provider_transaction_id', sa.String(), nullable=True),
        sa.Column('provider_response', sa.JSON(), nullable=True),
        sa.Column('provider_error', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('reference_id', sa.String(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )
    
    # Create payment_refunds table
    op.create_table(
        'payment_refunds',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('payment_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('provider_refund_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
    )
    
    # Create payment_providers table
    op.create_table(
        'payment_providers',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('display_name', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_test_mode', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('api_key', sa.String(), nullable=True),
        sa.Column('api_secret', sa.String(), nullable=True),
        sa.Column('merchant_id', sa.String(), nullable=True),
        sa.Column('callback_url', sa.String(), nullable=True),
        sa.Column('webhook_url', sa.String(), nullable=True),
        sa.Column('supports_irr', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('supports_usd', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('supports_eur', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('supports_refunds', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('transaction_fee_percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('transaction_fee_fixed', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('minimum_amount', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('maximum_amount', sa.Float(), nullable=True),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    
    # Create payment_webhooks table
    op.create_table(
        'payment_webhooks',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('provider_name', sa.String(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('signature', sa.String(), nullable=True),
        sa.Column('processed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    
    # Create indexes for better performance
    op.create_index('ix_payments_user_id', 'payments', ['user_id'])
    op.create_index('ix_payments_status', 'payments', ['status'])
    op.create_index('ix_payments_payment_method', 'payments', ['payment_method'])
    op.create_index('ix_payments_payment_type', 'payments', ['payment_type'])
    op.create_index('ix_payments_reference_id', 'payments', ['reference_id'])
    op.create_index('ix_payments_created_at', 'payments', ['created_at'])
    
    op.create_index('ix_payment_refunds_payment_id', 'payment_refunds', ['payment_id'])
    op.create_index('ix_payment_refunds_status', 'payment_refunds', ['status'])
    op.create_index('ix_payment_refunds_created_at', 'payment_refunds', ['created_at'])
    
    op.create_index('ix_payment_providers_name', 'payment_providers', ['name'])
    op.create_index('ix_payment_providers_is_active', 'payment_providers', ['is_active'])
    
    op.create_index('ix_payment_webhooks_provider_name', 'payment_webhooks', ['provider_name'])
    op.create_index('ix_payment_webhooks_processed', 'payment_webhooks', ['processed'])
    op.create_index('ix_payment_webhooks_created_at', 'payment_webhooks', ['created_at'])
    
    # Add foreign key constraints
    op.create_foreign_key('fk_payments_user_id', 'payments', 'users', ['user_id'], ['id'])
    op.create_foreign_key('fk_payment_refunds_payment_id', 'payment_refunds', 'payments', ['payment_id'], ['id'])

    # Create user_sessions table
    try:
        op.create_table(
            'user_sessions',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('device_id', sa.String(), nullable=True),
            sa.Column('user_agent', sa.String(), nullable=True),
            sa.Column('ip_address', sa.String(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('last_seen_at', sa.DateTime(), nullable=True),
            sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        )
        op.create_index('ix_user_sessions_user_id', 'user_sessions', ['user_id'])
        op.create_index('ix_user_sessions_created_at', 'user_sessions', ['created_at'])
    except Exception:
        pass


def downgrade() -> None:
    # Drop foreign key constraints
    op.drop_constraint('fk_payment_refunds_payment_id', 'payment_refunds', type_='foreignkey')
    op.drop_constraint('fk_payments_user_id', 'payments', type_='foreignkey')
    
    # Drop indexes
    op.drop_index('ix_payment_webhooks_created_at', table_name='payment_webhooks')
    op.drop_index('ix_payment_webhooks_processed', table_name='payment_webhooks')
    op.drop_index('ix_payment_webhooks_provider_name', table_name='payment_webhooks')
    
    op.drop_index('ix_payment_providers_is_active', table_name='payment_providers')
    op.drop_index('ix_payment_providers_name', table_name='payment_providers')
    
    op.drop_index('ix_payment_refunds_created_at', table_name='payment_refunds')
    op.drop_index('ix_payment_refunds_status', table_name='payment_refunds')
    op.drop_index('ix_payment_refunds_payment_id', table_name='payment_refunds')
    
    op.drop_index('ix_payments_created_at', table_name='payments')
    op.drop_index('ix_payments_reference_id', table_name='payments')
    op.drop_index('ix_payments_payment_type', table_name='payments')
    op.drop_index('ix_payments_payment_method', table_name='payments')
    op.drop_index('ix_payments_status', table_name='payments')
    op.drop_index('ix_payments_user_id', table_name='payments')
    
    # Drop tables
    op.drop_table('payment_webhooks')
    op.drop_table('payment_providers')
    op.drop_table('payment_refunds')
    op.drop_table('payments')

    # Drop user_sessions
    try:
        op.drop_index('ix_user_sessions_created_at', table_name='user_sessions')
        op.drop_index('ix_user_sessions_user_id', table_name='user_sessions')
        op.drop_table('user_sessions')
    except Exception:
        pass


