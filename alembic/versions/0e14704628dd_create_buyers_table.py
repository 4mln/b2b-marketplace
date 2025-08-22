"""create buyers table

Revision ID: 0e14704628dd
Revises: 6da58ab41fda
Create Date: 2025-08-21 17:25:15.498090
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0e14704628dd'
down_revision: Union[str, Sequence[str], None] = '6da58ab41fda'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Create enum type in Postgres
    subscription_enum = postgresql.ENUM(
        'FREE', 'BASIC', 'PREMIUM', name='subscription_type_enum'
    )
    subscription_enum.create(op.get_bind(), checkfirst=True)

    # 2. Alter sellers table with explicit USING clause
    with op.batch_alter_table('sellers', schema=None) as batch_op:
        batch_op.alter_column(
            'subscription_type',
            existing_type=sa.VARCHAR(length=50),
            type_=subscription_enum,
            existing_nullable=True,
            postgresql_using="subscription_type::subscription_type_enum"
        )

def downgrade() -> None:
    """Downgrade schema."""
    # 1. Revert sellers table back to VARCHAR
    with op.batch_alter_table('sellers', schema=None) as batch_op:
        batch_op.alter_column(
            'subscription_type',
            existing_type=sa.Enum(
                'FREE', 'BASIC', 'PREMIUM',
                name='subscription_type_enum'
            ),
            type_=sa.VARCHAR(length=50),
            existing_nullable=True,
            postgresql_using="subscription_type::VARCHAR"
        )

    # 2. Drop the enum type
    subscription_enum = postgresql.ENUM(
        'FREE', 'BASIC', 'PREMIUM', name='subscription_type_enum'
    )
    subscription_enum.drop(op.get_bind(), checkfirst=True)