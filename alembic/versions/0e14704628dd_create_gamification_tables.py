# alembic/versions/<timestamp>_create_gamification_tables.py
"""create badges and user_badges tables

Revision ID: gamification_001
Revises: 0e14704628dd  # put your latest migration ID here
Create Date: 2025-08-22 20:45:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'gamification_001'
down_revision = '0e14704628dd'
branch_labels = None
depends_on = None


def upgrade():
    # --------- Create badges table ---------
    op.create_table(
        'badges',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('points_required', sa.Integer, nullable=False, server_default='0'),
        sa.Column('icon_url', sa.String(512), nullable=True),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow, nullable=False),
    )

    # --------- Create user_badges table ---------
    op.create_table(
        'user_badges',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('badge_id', sa.Integer, sa.ForeignKey('badges.id', ondelete='CASCADE'), nullable=False),
        sa.Column('awarded_at', sa.DateTime, default=datetime.utcnow, nullable=False),
    )


def downgrade():
    op.drop_table('user_badges')
    op.drop_table('badges')