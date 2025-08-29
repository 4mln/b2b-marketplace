"""add phone to users and indices for otp

Revision ID: 3_add_phone_and_otp
Revises: 2_add_guild_id_to_products
Create Date: 2025-08-29 00:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3_add_phone_and_otp'
down_revision = '2_add_guild_id_to_products'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('phone', sa.String(), nullable=True))
    op.create_index('ix_users_phone', 'users', ['phone'], unique=True)
    # Optional helpful index for OTP expiry queries
    op.create_index('ix_users_otp_expiry', 'users', ['otp_expiry'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_users_otp_expiry', table_name='users')
    op.drop_index('ix_users_phone', table_name='users')
    op.drop_column('users', 'phone')


