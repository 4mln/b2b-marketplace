"""create cms pages

Revision ID: 13_create_cms_pages
Revises: 12_create_escrow
Create Date: 2025-08-29 01:58:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '13_create_cms_pages'
down_revision = '12_create_escrow'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'cms_pages',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('slug', sa.String(), unique=True, nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )


def downgrade() -> None:
    op.drop_table('cms_pages')












