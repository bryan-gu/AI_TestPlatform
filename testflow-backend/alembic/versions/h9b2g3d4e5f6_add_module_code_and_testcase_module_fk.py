"""add module code and testcase module_id FK

Revision ID: h9b2g3d4e5f6
Revises: g8a1f2c3d4e5
Create Date: 2026-06-06 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'h9b2g3d4e5f6'
down_revision = 'g8a1f2c3d4e5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. modules 加 code 列（英文缩写，如 SJZH、DL）
    op.add_column('modules', sa.Column('code', sa.String(50), nullable=True))

    # 部分唯一索引：code 非空时在 project_id 内唯一
    op.execute(
        "CREATE UNIQUE INDEX uq_modules_code_project "
        "ON modules (code, project_id) WHERE code IS NOT NULL"
    )

    # 2. testcases 加 module_id FK，指向 modules 表
    op.add_column('testcases', sa.Column('module_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_testcases_module_id', 'testcases', 'modules',
        ['module_id'], ['id'], ondelete='SET NULL'
    )


def downgrade() -> None:
    op.drop_constraint('fk_testcases_module_id', 'testcases', type_='foreignkey')
    op.drop_column('testcases', 'module_id')
    op.execute("DROP INDEX IF EXISTS uq_modules_code_project")
    op.drop_column('modules', 'code')
