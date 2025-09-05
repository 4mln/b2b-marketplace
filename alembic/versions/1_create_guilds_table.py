"""create guilds table

Revision ID: 1_create_guilds
Revises: 
Create Date: 2025-08-29 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '1_create_guilds'
down_revision = '67761632a53c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if not inspector.has_table('guilds'):
        op.create_table(
            'guilds',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('slug', sa.String(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('description', sa.String(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        )
        op.create_index('ix_guilds_slug', 'guilds', ['slug'], unique=True)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if inspector.has_table('guilds'):
        try:
            op.drop_index('ix_guilds_slug', table_name='guilds')
        except Exception:
            pass
        op.drop_table('guilds')



