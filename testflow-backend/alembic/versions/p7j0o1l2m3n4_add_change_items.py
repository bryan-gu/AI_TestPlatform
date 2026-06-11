"""add change_items table

Revision ID: p7j0o1l2m3n4
Revises: o6i9n0k1l2m3
Create Date: 2026-06-11 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'p7j0o1l2m3n4'
down_revision = 'o6i9n0k1l2m3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'change_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('sprint_id', sa.Integer(), nullable=False),
        sa.Column('source_doc_id', sa.Integer(), nullable=True),
        sa.Column('source_asset_id', sa.Integer(), nullable=True),
        sa.Column('module_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('description', sa.Text(), nullable=True, server_default=''),
        sa.Column('change_type', sa.String(30), nullable=True, server_default='unknown'),
        sa.Column('target_type', sa.String(40), nullable=True, server_default='feature'),
        sa.Column('target_id', sa.Integer(), nullable=True),
        sa.Column('priority', sa.String(10), nullable=True, server_default='中'),
        sa.Column('impact_level', sa.String(10), nullable=True, server_default='中'),
        sa.Column('status', sa.String(30), nullable=True, server_default='open'),
        sa.Column('before_snapshot', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('after_snapshot', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('evidence', sa.Text(), nullable=True, server_default=''),
        sa.Column('confidence', sa.Integer(), nullable=True, server_default='80'),
        sa.Column('fingerprint', sa.String(200), nullable=True, server_default=''),
        sa.Column('raw_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['sprint_id'], ['sprints.id']),
        sa.ForeignKeyConstraint(['source_doc_id'], ['documents.id']),
        sa.ForeignKeyConstraint(['source_asset_id'], ['knowledge_assets.id']),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_change_items_project_sprint', 'change_items', ['project_id', 'sprint_id'])
    op.create_index('ix_change_items_sprint_status', 'change_items', ['sprint_id', 'status'])
    op.create_index('ix_change_items_source_doc', 'change_items', ['source_doc_id'])
    op.create_index('ix_change_items_source_asset', 'change_items', ['source_asset_id'])
    op.create_index('ix_change_items_module', 'change_items', ['module_id'])
    op.create_index('ix_change_items_change_type', 'change_items', ['change_type'])
    op.create_index('ix_change_items_target', 'change_items', ['target_type', 'target_id'])
    op.create_index('ix_change_items_fingerprint', 'change_items', ['fingerprint'])


def downgrade() -> None:
    op.drop_index('ix_change_items_fingerprint', table_name='change_items')
    op.drop_index('ix_change_items_target', table_name='change_items')
    op.drop_index('ix_change_items_change_type', table_name='change_items')
    op.drop_index('ix_change_items_module', table_name='change_items')
    op.drop_index('ix_change_items_source_asset', table_name='change_items')
    op.drop_index('ix_change_items_source_doc', table_name='change_items')
    op.drop_index('ix_change_items_sprint_status', table_name='change_items')
    op.drop_index('ix_change_items_project_sprint', table_name='change_items')
    op.drop_table('change_items')
