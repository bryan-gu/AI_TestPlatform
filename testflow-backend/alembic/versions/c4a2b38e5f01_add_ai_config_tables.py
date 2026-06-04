"""add_ai_config_tables

Revision ID: c4a2b38e5f01
Revises: b3f1a27c8d04
Create Date: 2026-06-04 22:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4a2b38e5f01'
down_revision: Union[str, None] = 'b3f1a27c8d04'
branch_labels: Union[str, Sequence[str]] = None
depends_on: Union[str, Sequence[str]] = None


def upgrade() -> None:
    # AI 服务商配置表
    op.create_table(
        'ai_providers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('provider_type', sa.String(50), nullable=False, comment='服务商类型'),
        sa.Column('name', sa.String(100), nullable=False, comment='显示名称'),
        sa.Column('api_key', sa.String(500), nullable=False, comment='API Key'),
        sa.Column('model', sa.String(100), nullable=False, comment='模型名称'),
        sa.Column('endpoint_url', sa.String(500), nullable=True, comment='自定义端点'),
        sa.Column('temperature', sa.Float(), nullable=True, comment='温度参数'),
        sa.Column('max_tokens', sa.Integer(), nullable=True, comment='最大 Token 数'),
        sa.Column('status', sa.String(20), nullable=True, comment='状态'),
        sa.Column('last_call_at', sa.DateTime(), nullable=True, comment='最近调用时间'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # 模型分配策略表
    op.create_table(
        'model_strategies',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('task_type', sa.String(50), nullable=False, comment='任务类型'),
        sa.Column('provider_id', sa.Integer(), nullable=True, comment='关联服务商'),
        sa.Column('model_name', sa.String(100), nullable=False, comment='模型名称'),
        sa.Column('temperature', sa.Float(), nullable=True, comment='温度参数'),
        sa.ForeignKeyConstraint(['provider_id'], ['ai_providers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('task_type'),
    )

    # AI 全局参数配置表
    op.create_table(
        'ai_global_configs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('key', sa.String(100), nullable=False, comment='参数键名'),
        sa.Column('value', sa.Text(), nullable=False, comment='参数值'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key'),
    )

    # AI 调用日志表
    op.create_table(
        'ai_call_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('task_type', sa.String(50), nullable=True, comment='任务类型'),
        sa.Column('model', sa.String(100), nullable=True, comment='调用的模型'),
        sa.Column('provider_id', sa.Integer(), nullable=True, comment='关联服务商'),
        sa.Column('input_tokens', sa.Integer(), nullable=True, comment='输入 Token'),
        sa.Column('output_tokens', sa.Integer(), nullable=True, comment='输出 Token'),
        sa.Column('duration_ms', sa.Integer(), nullable=True, comment='耗时 ms'),
        sa.Column('status', sa.String(20), nullable=True, comment='状态'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['provider_id'], ['ai_providers.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('ai_call_logs')
    op.drop_table('ai_global_configs')
    op.drop_table('model_strategies')
    op.drop_table('ai_providers')
