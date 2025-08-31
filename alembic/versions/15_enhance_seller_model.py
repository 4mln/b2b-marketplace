"""enhance seller model with storefront features

Revision ID: 15_enhance_seller_model
Revises: 14_enhance_user_profiles
Create Date: 2025-08-29 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '15_enhance_seller_model'
down_revision = '14_enhance_user_profiles'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to sellers table
    op.add_column('sellers', sa.Column('email', sa.String(), nullable=True))
    op.add_column('sellers', sa.Column('phone', sa.String(), nullable=True))
    op.add_column('sellers', sa.Column('subscription', sa.String(), nullable=False, server_default='basic'))
    op.add_column('sellers', sa.Column('store_url', sa.String(), nullable=True))
    op.add_column('sellers', sa.Column('store_policies', sa.JSON(), nullable=True))
    op.add_column('sellers', sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('sellers', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('sellers', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')))
    op.add_column('sellers', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')))
    
    # Drop old subscription_type column if it exists
    try:
        op.drop_column('sellers', 'subscription_type')
    except:
        pass  # Column might not exist
    
    # Create indexes for better performance
    op.create_index('ix_sellers_subscription', 'sellers', ['subscription'])
    op.create_index('ix_sellers_is_featured', 'sellers', ['is_featured'])
    op.create_index('ix_sellers_is_verified', 'sellers', ['is_verified'])
    op.create_index('ix_sellers_created_at', 'sellers', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_sellers_created_at', table_name='sellers')
    op.drop_index('ix_sellers_is_verified', table_name='sellers')
    op.drop_index('ix_sellers_is_featured', table_name='sellers')
    op.drop_index('ix_sellers_subscription', table_name='sellers')
    
    # Drop columns
    op.drop_column('sellers', 'updated_at')
    op.drop_column('sellers', 'created_at')
    op.drop_column('sellers', 'is_verified')
    op.drop_column('sellers', 'is_featured')
    op.drop_column('sellers', 'store_policies')
    op.drop_column('sellers', 'store_url')
    op.drop_column('sellers', 'subscription')
    op.drop_column('sellers', 'phone')
    op.drop_column('sellers', 'email')
    
    # Recreate old subscription_type column
    op.add_column('sellers', sa.Column('subscription_type', sa.String(), nullable=False))


