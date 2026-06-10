"""add trace links table

Revision ID: n5h8m9j0k1l2
Revises: m4g7l8i9j0k1
Create Date: 2026-06-10 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'n5h8m9j0k1l2'
down_revision = 'm4g7l8i9j0k1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'trace_links',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('sprint_id', sa.Integer(), nullable=True),
        sa.Column('source_type', sa.String(40), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('target_type', sa.String(40), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('relation_type', sa.String(40), nullable=False),
        sa.Column('confidence', sa.Integer(), nullable=True, server_default='100'),
        sa.Column('evidence', sa.Text(), nullable=True, server_default=''),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(30), nullable=True, server_default='active'),
        sa.Column('created_by', sa.String(30), nullable=True, server_default='system'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['sprint_id'], ['sprints.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'project_id', 'sprint_id', 'source_type', 'source_id',
            'target_type', 'target_id', 'relation_type',
            name='uq_trace_links_unique_relation'
        ),
    )
    op.create_index('ix_trace_links_project_sprint', 'trace_links', ['project_id', 'sprint_id'])
    op.create_index('ix_trace_links_source', 'trace_links', ['source_type', 'source_id'])
    op.create_index('ix_trace_links_target', 'trace_links', ['target_type', 'target_id'])
    op.create_index('ix_trace_links_relation', 'trace_links', ['relation_type'])
    op.create_index('ix_trace_links_source_relation', 'trace_links', ['source_type', 'source_id', 'relation_type'])
    op.create_index('ix_trace_links_target_relation', 'trace_links', ['target_type', 'target_id', 'relation_type'])


def downgrade() -> None:
    op.drop_index('ix_trace_links_target_relation', table_name='trace_links')
    op.drop_index('ix_trace_links_source_relation', table_name='trace_links')
    op.drop_index('ix_trace_links_relation', table_name='trace_links')
    op.drop_index('ix_trace_links_target', table_name='trace_links')
    op.drop_index('ix_trace_links_source', table_name='trace_links')
    op.drop_index('ix_trace_links_project_sprint', table_name='trace_links')
    op.drop_table('trace_links')
