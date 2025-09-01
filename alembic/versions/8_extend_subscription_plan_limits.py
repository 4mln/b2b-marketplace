"""extend subscription plan limits

Revision ID: 8_extend_subscription_plan_limits
Revises: 7_create_compliance
Create Date: 2025-08-29 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8_extend_subscription_plan_limits'
down_revision = '7_create_compliance'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('subscription_plans', sa.Column('max_products', sa.Integer(), nullable=True))
    op.add_column('subscription_plans', sa.Column('max_rfqs', sa.Integer(), nullable=True))
    op.add_column('subscription_plans', sa.Column('boost_multiplier', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('subscription_plans', 'boost_multiplier')
    op.drop_column('subscription_plans', 'max_rfqs')
    op.drop_column('subscription_plans', 'max_products')








