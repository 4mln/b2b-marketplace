"""create compliance tables

Revision ID: 7_create_compliance
Revises: 6_create_ads
Create Date: 2025-08-29 00:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7_create_compliance'
down_revision = '6_create_ads'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'banned_items',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('keyword', sa.String(), unique=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('actor', sa.String(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('entity', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('banned_items')












