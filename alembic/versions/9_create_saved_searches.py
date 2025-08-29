"""create saved searches table

Revision ID: 9_create_saved_searches
Revises: 8_extend_subscription_plan_limits
Create Date: 2025-08-29 01:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9_create_saved_searches'
down_revision = '8_extend_subscription_plan_limits'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'saved_searches',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('query', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )


def downgrade() -> None:
    op.drop_table('saved_searches')


