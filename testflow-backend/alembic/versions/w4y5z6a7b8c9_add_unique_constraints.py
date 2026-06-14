"""add unique constraints (partial, active only)

Revision ID: w4y5z6a7b8c9
Revises: v3y4s5t6u7v8
Create Date: 2026-06-15

为 testcases / api_endpoints 补 active 唯一约束（partial unique index，仅 is_deleted=false），
保障 upsert 幂等、防止重复实体。trace_links 六元组唯一约束在 n5h8m9j0k1l2 已建，此处不补。

软删除行（is_deleted=true）不参与唯一，保留审计历史；迁移前先清洗 active 重复（保留最新 id）。
"""
from alembic import op
import sqlalchemy as sa


revision = 'w4y5z6a7b8c9'
down_revision = 'v3y4s5t6u7v8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. 清洗 active testcases 重复（同 project+sprint+case_no，保留最新 id）
    op.execute(sa.text("""
        DELETE FROM testcases
        WHERE is_deleted = false
          AND case_no IS NOT NULL AND case_no <> ''
          AND id NOT IN (
              SELECT max(id) FROM testcases
              WHERE is_deleted = false AND case_no IS NOT NULL AND case_no <> ''
              GROUP BY project_id, sprint_id, case_no
          )
    """))
    # 2. 清洗 active api_endpoints 重复（同 project+sprint+method+path，保留最新 id）
    op.execute(sa.text("""
        DELETE FROM api_endpoints
        WHERE is_deleted = false
          AND id NOT IN (
              SELECT max(id) FROM api_endpoints
              WHERE is_deleted = false
              GROUP BY project_id, sprint_id, method, path
          )
    """))
    # 3. partial unique index（仅 active 行唯一，软删历史不冲突）
    op.create_index(
        'uq_testcases_active_case_no', 'testcases',
        ['project_id', 'sprint_id', 'case_no'],
        unique=True,
        postgresql_where=sa.text('is_deleted = false'),
    )
    op.create_index(
        'uq_api_endpoints_active_method_path', 'api_endpoints',
        ['project_id', 'sprint_id', 'method', 'path'],
        unique=True,
        postgresql_where=sa.text('is_deleted = false'),
    )


def downgrade() -> None:
    op.drop_index('uq_api_endpoints_active_method_path', table_name='api_endpoints')
    op.drop_index('uq_testcases_active_case_no', table_name='testcases')
