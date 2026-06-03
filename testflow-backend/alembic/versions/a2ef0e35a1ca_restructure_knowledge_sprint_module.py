"""restructure_knowledge_sprint_module

Revision ID: a2ef0e35a1ca
Revises: a01dc2deacf3
Create Date: 2026-06-04 00:59:27.769800
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'a2ef0e35a1ca'
down_revision: Union[str, None] = 'a01dc2deacf3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ===== 1. 创建新表 =====
    op.create_table('modules',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('color', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('sprints',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('is_all', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # ===== 2. 删除旧 documents 表（含数据，Clean Break）=====
    op.drop_table('documents')

    # ===== 3. 删除旧 folders 和 knowledge_bases =====
    op.drop_table('folders')
    op.drop_table('knowledge_bases')

    # ===== 4. 重建 documents 表（新 schema）=====
    op.create_table('documents',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('file_type', sa.String(length=20), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('sprint_id', sa.Integer(), nullable=False),
        sa.Column('uploader_id', sa.Integer(), nullable=True),
        sa.Column('version', sa.String(length=20), nullable=True),
        sa.Column('content_preview', sa.Text(), nullable=True),
        sa.Column('ai_summary', sa.Text(), nullable=True),
        sa.Column('keywords', sa.JSON(), nullable=True),
        sa.Column('module_ids', sa.JSON(), nullable=True),
        sa.Column('ai_status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['sprint_id'], ['sprints.id']),
        sa.ForeignKeyConstraint(['uploader_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # ===== 5. testcases 新增 3 字段 =====
    op.add_column('testcases', sa.Column('preconditions', sa.Text(), nullable=True))
    op.add_column('testcases', sa.Column('test_steps', sa.Text(), nullable=True))
    op.add_column('testcases', sa.Column('expected_result', sa.Text(), nullable=True))

    # ===== 6. reports 新增 4 字段 + FK =====
    op.add_column('reports', sa.Column('report_type', sa.String(length=20), nullable=True))
    op.add_column('reports', sa.Column('test_scope', sa.Text(), nullable=True))
    op.add_column('reports', sa.Column('approved_by', sa.Integer(), nullable=True))
    op.add_column('reports', sa.Column('approved_at', sa.DateTime(), nullable=True))
    op.create_foreign_key('fk_reports_approved_by', 'reports', 'users', ['approved_by'], ['id'])


def downgrade() -> None:
    # ===== 回滚 reports =====
    op.drop_constraint('fk_reports_approved_by', 'reports', type_='foreignkey')
    op.drop_column('reports', 'approved_at')
    op.drop_column('reports', 'approved_by')
    op.drop_column('reports', 'test_scope')
    op.drop_column('reports', 'report_type')

    # ===== 回滚 testcases =====
    op.drop_column('testcases', 'expected_result')
    op.drop_column('testcases', 'test_steps')
    op.drop_column('testcases', 'preconditions')

    # ===== 回滚 documents（新 → 旧）=====
    op.drop_table('documents')

    # ===== 恢复旧表 =====
    op.create_table('knowledge_bases',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
        sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column('project_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('creator_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], name='knowledge_bases_creator_id_fkey'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name='knowledge_bases_project_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='knowledge_bases_pkey'),
    )
    op.create_table('folders',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
        sa.Column('knowledge_base_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['knowledge_base_id'], ['knowledge_bases.id'], name='folders_knowledge_base_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='folders_pkey'),
    )
    op.create_table('documents',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('name', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
        sa.Column('file_path', sa.VARCHAR(length=500), autoincrement=False, nullable=True),
        sa.Column('file_type', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
        sa.Column('file_size', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('folder_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('uploader_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['folder_id'], ['folders.id'], name='documents_folder_id_fkey'),
        sa.ForeignKeyConstraint(['uploader_id'], ['users.id'], name='documents_uploader_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='documents_pkey'),
    )

    # ===== 删除新表 =====
    op.drop_table('sprints')
    op.drop_table('modules')
