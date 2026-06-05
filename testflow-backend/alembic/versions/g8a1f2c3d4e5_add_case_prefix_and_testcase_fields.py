"""add case_prefix to projects, module/test_data/actual_result to testcases, widen case_no

Revision ID: g8a1f2c3d4e5
Revises: f7d5e68a8b04
Create Date: 2026-06-05 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'g8a1f2c3d4e5'
down_revision = 'f7d5e68a8b04'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add case_prefix to projects
    op.add_column('projects', sa.Column('case_prefix', sa.String(20), nullable=True))
    op.create_unique_constraint('uq_projects_case_prefix', 'projects', ['case_prefix'])

    # 2. Add new columns to testcases
    op.add_column('testcases', sa.Column('module', sa.String(50), nullable=True))
    op.add_column('testcases', sa.Column('test_data', sa.Text(), nullable=True))
    op.add_column('testcases', sa.Column('actual_result', sa.Text(), nullable=True))

    # 3. Widen case_no from varchar(20) to varchar(60), drop unique constraint
    op.alter_column('testcases', 'case_no',
                    existing_type=sa.String(20),
                    type_=sa.String(60),
                    existing_nullable=False)
    op.drop_constraint('testcases_case_no_key', 'testcases', type_='unique')


def downgrade() -> None:
    op.create_unique_constraint('testcases_case_no_key', 'testcases', ['case_no'])
    op.alter_column('testcases', 'case_no',
                    existing_type=sa.String(60),
                    type_=sa.String(20),
                    existing_nullable=False)
    op.drop_column('testcases', 'actual_result')
    op.drop_column('testcases', 'test_data')
    op.drop_column('testcases', 'module')
    op.drop_constraint('uq_projects_case_prefix', 'projects', type_='unique')
    op.drop_column('projects', 'case_prefix')
