"""enhance user profiles with business information and audit trail

Revision ID: 14_enhance_user_profiles
Revises: 13_create_cms_pages
Create Date: 2025-08-29 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '14_enhance_user_profiles'
down_revision = '13_create_cms_pages'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add business information fields to users table
    op.add_column('users', sa.Column('business_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('business_registration_number', sa.String(), nullable=True))
    op.add_column('users', sa.Column('business_tax_id', sa.String(), nullable=True))
    op.add_column('users', sa.Column('business_type', sa.String(), nullable=True))
    op.add_column('users', sa.Column('business_industry', sa.String(), nullable=True))
    op.add_column('users', sa.Column('business_description', sa.Text(), nullable=True))
    
    # Add contact details
    op.add_column('users', sa.Column('business_phones', sa.JSON(), nullable=True))
    op.add_column('users', sa.Column('business_emails', sa.JSON(), nullable=True))
    op.add_column('users', sa.Column('website', sa.String(), nullable=True))
    op.add_column('users', sa.Column('telegram_id', sa.String(), nullable=True))
    op.add_column('users', sa.Column('whatsapp_id', sa.String(), nullable=True))
    
    # Add addresses and bank accounts
    op.add_column('users', sa.Column('business_addresses', sa.JSON(), nullable=True))
    op.add_column('users', sa.Column('bank_accounts', sa.JSON(), nullable=True))
    
    # Add media fields
    op.add_column('users', sa.Column('business_photo', sa.String(), nullable=True))
    op.add_column('users', sa.Column('banner_photo', sa.String(), nullable=True))
    
    # Add privacy and preferences
    op.add_column('users', sa.Column('privacy_settings', sa.JSON(), nullable=True))
    op.add_column('users', sa.Column('notification_preferences', sa.JSON(), nullable=True))
    
    # Add audit trail fields
    op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('profile_completion_percentage', sa.Integer(), nullable=True, server_default='0'))
    
    # Add KYC fields
    op.add_column('users', sa.Column('kyc_verified_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('kyc_verified_by', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('kyc_rejection_reason', sa.Text(), nullable=True))
    
    # Create user profile changes audit table
    op.create_table(
        'user_profile_changes',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('changed_by', sa.Integer(), nullable=False),
        sa.Column('field_name', sa.String(), nullable=False),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('change_type', sa.String(), nullable=False),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    
    # Create indexes for better performance
    op.create_index('ix_user_profile_changes_user_id', 'user_profile_changes', ['user_id'])
    op.create_index('ix_user_profile_changes_created_at', 'user_profile_changes', ['created_at'])
    op.create_index('ix_users_business_name', 'users', ['business_name'])
    op.create_index('ix_users_business_type', 'users', ['business_type'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_users_business_type', table_name='users')
    op.drop_index('ix_users_business_name', table_name='users')
    op.drop_index('ix_user_profile_changes_created_at', table_name='user_profile_changes')
    op.drop_index('ix_user_profile_changes_user_id', table_name='user_profile_changes')
    
    # Drop audit table
    op.drop_table('user_profile_changes')
    
    # Drop columns from users table
    op.drop_column('users', 'kyc_rejection_reason')
    op.drop_column('users', 'kyc_verified_by')
    op.drop_column('users', 'kyc_verified_at')
    op.drop_column('users', 'profile_completion_percentage')
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'notification_preferences')
    op.drop_column('users', 'privacy_settings')
    op.drop_column('users', 'banner_photo')
    op.drop_column('users', 'business_photo')
    op.drop_column('users', 'bank_accounts')
    op.drop_column('users', 'business_addresses')
    op.drop_column('users', 'whatsapp_id')
    op.drop_column('users', 'telegram_id')
    op.drop_column('users', 'website')
    op.drop_column('users', 'business_emails')
    op.drop_column('users', 'business_phones')
    op.drop_column('users', 'business_description')
    op.drop_column('users', 'business_industry')
    op.drop_column('users', 'business_type')
    op.drop_column('users', 'business_tax_id')
    op.drop_column('users', 'business_registration_number')
    op.drop_column('users', 'business_name')
