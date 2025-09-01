"""create ratings table

Revision ID: 5_create_ratings
Revises: 4_create_rfqs_and_quotes
Create Date: 2025-08-29 00:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5_create_ratings'
down_revision = '4_create_rfqs_and_quotes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'ratings',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('order_id', sa.Integer(), sa.ForeignKey('orders.id'), nullable=False),
        sa.Column('rater_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('ratee_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('quality', sa.Float(), nullable=False),
        sa.Column('timeliness', sa.Float(), nullable=False),
        sa.Column('communication', sa.Float(), nullable=False),
        sa.Column('reliability', sa.Float(), nullable=False),
        sa.Column('comment', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )


def downgrade() -> None:
    op.drop_table('ratings')








