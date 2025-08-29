"""add product status field

Revision ID: 11_add_product_status
Revises: 10_create_search_events
Create Date: 2025-08-29 01:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '11_add_product_status'
down_revision = '10_create_search_events'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('products', sa.Column('status', sa.String(), server_default='pending', nullable=False))


def downgrade() -> None:
    op.drop_column('products', 'status')


