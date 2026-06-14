"""add import jobs

Revision ID: v3y4s5t6u7v8
Revises: u2x3r4s5t6u7
Create Date: 2026-06-15
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = 'v3y4s5t6u7v8'
down_revision = 'u2x3r4s5t6u7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'import_jobs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('root_path', sa.String(length=500), nullable=False),
        sa.Column('job_type', sa.String(length=40), nullable=True, server_default='local_project'),
        sa.Column('status', sa.String(length=30), nullable=True, server_default='pending'),
        sa.Column('dry_run', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('total_files', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('processed_files', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('success_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('failed_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('result_summary', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('warnings', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('errors', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_import_jobs_project', 'import_jobs', ['project_id'])
    op.create_index('ix_import_jobs_status', 'import_jobs', ['status'])


def downgrade() -> None:
    op.drop_index('ix_import_jobs_status', table_name='import_jobs')
    op.drop_index('ix_import_jobs_project', table_name='import_jobs')
    op.drop_table('import_jobs')
