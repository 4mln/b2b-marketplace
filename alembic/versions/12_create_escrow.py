"""create escrow table

Revision ID: 12_create_escrow
Revises: 11_add_product_status
Create Date: 2025-08-29 01:48:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '12_create_escrow'
down_revision = '11_add_product_status'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'escrows',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('order_id', sa.Integer(), sa.ForeignKey('orders.id'), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(), nullable=False, server_default='IRR'),
        sa.Column('status', sa.String(), nullable=False, server_default='held'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )


def downgrade() -> None:
    op.drop_table('escrows')








