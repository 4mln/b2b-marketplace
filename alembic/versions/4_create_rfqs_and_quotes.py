"""create rfqs and quotes

Revision ID: 4_create_rfqs_and_quotes
Revises: 3_add_phone_and_otp
Create Date: 2025-08-29 00:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4_create_rfqs_and_quotes'
down_revision = '3_add_phone_and_otp'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'rfqs',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('buyer_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('specifications', sa.JSON(), nullable=True),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('target_price', sa.Float(), nullable=True),
        sa.Column('delivery', sa.String(), nullable=True),
        sa.Column('expiry', sa.DateTime(timezone=True), nullable=True),
        sa.Column('attachments', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'quotes',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('rfq_id', sa.Integer(), sa.ForeignKey('rfqs.id'), nullable=False),
        sa.Column('seller_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('terms', sa.String(), nullable=True),
        sa.Column('attachments', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='sent'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )


def downgrade() -> None:
    op.drop_table('quotes')
    op.drop_table('rfqs')








