"""remove temperature columns from ai_providers and model_strategies

Revision ID: f7d5e68a8b04
Revises: e6c4d57f7b03
Create Date: 2026-06-04 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7d5e68a8b04'
down_revision = 'e6c4d57f7b03'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('ai_providers', 'temperature')
    op.drop_column('model_strategies', 'temperature')


def downgrade() -> None:
    op.add_column('model_strategies', sa.Column('temperature', sa.Float(), nullable=True, comment='温度参数'))
    op.add_column('ai_providers', sa.Column('temperature', sa.Float(), nullable=True, comment='温度参数'))
