"""create ads tables

Revision ID: 6_create_ads
Revises: 5_create_ratings
Create Date: 2025-08-29 00:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6_create_ads'
down_revision = '5_create_ratings'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'ad_campaigns',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('budget', sa.Float(), nullable=False),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('active', sa.Boolean(), server_default=sa.text('1'), nullable=False),
        sa.Column('targeting', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'ad_placements',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('campaign_id', sa.Integer(), sa.ForeignKey('ad_campaigns.id'), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('budget_spent', sa.Float(), server_default=sa.text('0'), nullable=False),
        sa.Column('metrics', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )


def downgrade() -> None:
    op.drop_table('ad_placements')
    op.drop_table('ad_campaigns')


