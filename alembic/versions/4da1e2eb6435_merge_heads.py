"""merge heads

Revision ID: 4da1e2eb6435
Revises: gamification_001, 23, wallet_tables
Create Date: 2025-09-05 09:27:24.094613

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4da1e2eb6435'
down_revision: Union[str, Sequence[str], None] = ('gamification_001', '23', 'wallet_tables')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
