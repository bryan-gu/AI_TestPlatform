"""add call log error fields

Revision ID: i0c3h4e5f6g7
Revises: h9b2g3d4e5f6
Create Date: 2026-06-06 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'i0c3h4e5f6g7'
down_revision = 'h9b2g3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('ai_call_logs', sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'))
    op.add_column('ai_call_logs', sa.Column('request_summary', sa.String(500), nullable=True, comment='请求摘要'))


def downgrade() -> None:
    op.drop_column('ai_call_logs', 'request_summary')
    op.drop_column('ai_call_logs', 'error_message')
