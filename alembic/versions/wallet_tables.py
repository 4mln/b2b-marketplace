"""Add wallet and transaction tables

Revision ID: wallet_tables
Revises: 
Create Date: 2023-06-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'wallet_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    # Create wallets table if it does not exist
    if not inspector.has_table('wallets'):
        op.create_table(
            'wallets',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('currency', sa.String(), nullable=False),
            sa.Column('currency_type', sa.String(), nullable=False),
            sa.Column('balance', sa.Float(), nullable=False, default=0.0),
            sa.Column('is_active', sa.Boolean(), default=True),
            sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_wallets_id'), 'wallets', ['id'], unique=False)

    # Create transactions table if it does not exist
    if not inspector.has_table('transactions'):
        op.create_table(
            'transactions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('wallet_id', sa.Integer(), nullable=False),
            sa.Column('amount', sa.Float(), nullable=False),
            sa.Column('transaction_type', sa.String(), nullable=False),
            sa.Column('reference', sa.String(), nullable=True),
            sa.Column('description', sa.String(), nullable=True),
            sa.Column('status', sa.String(), default='pending'),
            sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
            sa.ForeignKeyConstraint(['wallet_id'], ['wallets.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_transactions_id'), 'transactions', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_transactions_id'), table_name='transactions')
    op.drop_table('transactions')
    op.drop_index(op.f('ix_wallets_id'), table_name='wallets')
    op.drop_table('wallets')