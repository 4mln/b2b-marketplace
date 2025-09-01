"""create search events table

Revision ID: 10_create_search_events
Revises: 9_create_saved_searches
Create Date: 2025-08-29 01:28:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '10_create_search_events'
down_revision = '9_create_saved_searches'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'search_events',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('query', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )


def downgrade() -> None:
    op.drop_table('search_events')








