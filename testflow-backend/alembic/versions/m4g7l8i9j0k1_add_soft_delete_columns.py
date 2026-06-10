"""add soft delete columns

Revision ID: m4g7l8i9j0k1
Revises: l3f6k7h8i9j0
Create Date: 2026-06-10 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'm4g7l8i9j0k1'
down_revision = 'l3f6k7h8i9j0'
branch_labels = None
depends_on = None

# 需要新增软删除字段的表
_TABLES = [
    'projects',
    'sprints',
    'modules',
    'testcases',
    'feature_points',
    'graphs',
    'documents',
]


def upgrade() -> None:
    for table in _TABLES:
        op.add_column(table, sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.false()))
        op.add_column(table, sa.Column('deleted_at', sa.DateTime(), nullable=True))

    # projects.case_prefix：把全局唯一约束改为「仅未删除时唯一」的部分唯一索引
    op.drop_constraint('uq_projects_case_prefix', 'projects', type_='unique')
    op.execute(
        "CREATE UNIQUE INDEX uq_projects_case_prefix "
        "ON projects (case_prefix) WHERE case_prefix IS NOT NULL AND is_deleted = false"
    )

    # modules：把 (code, project_id) 部分唯一索引追加 is_deleted = false 条件
    op.execute("DROP INDEX IF EXISTS uq_modules_code_project")
    op.execute(
        "CREATE UNIQUE INDEX uq_modules_code_project "
        "ON modules (code, project_id) WHERE code IS NOT NULL AND is_deleted = false"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_modules_code_project")
    op.execute(
        "CREATE UNIQUE INDEX uq_modules_code_project "
        "ON modules (code, project_id) WHERE code IS NOT NULL"
    )

    op.execute("DROP INDEX IF EXISTS uq_projects_case_prefix")
    op.create_unique_constraint('uq_projects_case_prefix', 'projects', ['case_prefix'])

    for table in _TABLES:
        op.drop_column(table, 'deleted_at')
        op.drop_column(table, 'is_deleted')
