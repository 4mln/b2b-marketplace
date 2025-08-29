"""add guild_id to products

Revision ID: 2_add_guild_id_to_products
Revises: 1_create_guilds
Create Date: 2025-08-29 00:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2_add_guild_id_to_products'
down_revision = '1_create_guilds'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('products', sa.Column('guild_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_products_guild_id_guilds', 'products', 'guilds', ['guild_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    op.drop_constraint('fk_products_guild_id_guilds', 'products', type_='foreignkey')
    op.drop_column('products', 'guild_id')


