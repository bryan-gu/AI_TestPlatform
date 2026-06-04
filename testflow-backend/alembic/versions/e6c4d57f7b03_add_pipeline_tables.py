"""add pipeline tables

Revision ID: e6c4d57f7b03
Revises: d5b3c49f6a02
Create Date: 2026-06-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e6c4d57f7b03'
down_revision: Union[str, None] = 'd5b3c49f6a02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # pipeline_executions
    op.create_table(
        'pipeline_executions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('sprint_id', sa.Integer(), nullable=True),
        sa.Column('mode', sa.String(20), nullable=False, server_default='full'),
        sa.Column('status', sa.String(20), nullable=False, server_default='waiting'),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('total_duration_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['sprint_id'], ['sprints.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # pipeline_stages
    op.create_table(
        'pipeline_stages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('execution_id', sa.Integer(), nullable=False),
        sa.Column('stage_no', sa.Integer(), nullable=False),
        sa.Column('stage_name', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='waiting'),
        sa.Column('model', sa.String(100), nullable=True),
        sa.Column('input_tokens', sa.Integer(), server_default='0'),
        sa.Column('output_tokens', sa.Integer(), server_default='0'),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('result_summary', sa.JSON(), server_default='{}'),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['execution_id'], ['pipeline_executions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('pipeline_stages')
    op.drop_table('pipeline_executions')
