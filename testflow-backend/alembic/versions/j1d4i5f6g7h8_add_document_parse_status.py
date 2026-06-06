"""add document parse_status

Revision ID: j1d4i5f6g7h8
Revises: i0c3h4e5f6g7
Create Date: 2026-06-07 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'j1d4i5f6g7h8'
down_revision = 'i0c3h4e5f6g7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 新增 parse_status 列
    op.add_column('documents', sa.Column('parse_status', sa.String(20), nullable=True, comment='MinerU解析状态'))

    # 将 parse_status 默认值设为"待解析"
    op.execute("UPDATE documents SET parse_status = '待解析' WHERE parse_status IS NULL")

    # 将已有 ai_status 中的解析相关状态回归为"待分析"
    op.execute("UPDATE documents SET ai_status = '待分析' WHERE ai_status IN ('分析中', '已分析')")


def downgrade() -> None:
    op.drop_column('documents', 'parse_status')
