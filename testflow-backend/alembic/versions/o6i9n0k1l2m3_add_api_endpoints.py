"""add api_endpoints and testcase_api_endpoints tables

Revision ID: o6i9n0k1l2m3
Revises: n5h8m9j0k1l2
Create Date: 2026-06-11 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'o6i9n0k1l2m3'
down_revision = 'n5h8m9j0k1l2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # api_endpoints 表
    op.create_table(
        'api_endpoints',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('sprint_id', sa.Integer(), nullable=True),
        sa.Column('source_asset_id', sa.Integer(), nullable=True),
        sa.Column('module_id', sa.Integer(), nullable=True),
        sa.Column('method', sa.String(10), nullable=False),
        sa.Column('path', sa.String(500), nullable=False),
        sa.Column('summary', sa.String(500), nullable=True, server_default=''),
        sa.Column('description', sa.Text(), nullable=True, server_default=''),
        sa.Column('tag', sa.String(100), nullable=True, server_default=''),
        sa.Column('operation_id', sa.String(200), nullable=True, server_default=''),
        sa.Column('status', sa.String(30), nullable=True, server_default='active'),
        sa.Column('priority', sa.String(10), nullable=True, server_default='中'),
        sa.Column('auth_required', sa.Boolean(), nullable=True),
        sa.Column('request_schema', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('response_schema', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('parameters', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('error_codes', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('version', sa.String(20), nullable=True, server_default='v1'),
        sa.Column('fingerprint', sa.String(200), nullable=True, server_default=''),
        sa.Column('raw_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['sprint_id'], ['sprints.id']),
        sa.ForeignKeyConstraint(['source_asset_id'], ['knowledge_assets.id']),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'source_asset_id', 'method', 'path',
            name='uq_api_endpoints_source_method_path',
        ),
    )
    op.create_index('ix_api_endpoints_project_sprint', 'api_endpoints', ['project_id', 'sprint_id'])
    op.create_index('ix_api_endpoints_source_asset', 'api_endpoints', ['source_asset_id'])
    op.create_index('ix_api_endpoints_method_path', 'api_endpoints', ['method', 'path'])
    op.create_index('ix_api_endpoints_status', 'api_endpoints', ['status'])
    op.create_index('ix_api_endpoints_tag', 'api_endpoints', ['tag'])
    op.create_index('ix_api_endpoints_fingerprint', 'api_endpoints', ['fingerprint'])

    # testcase_api_endpoints 表
    op.create_table(
        'testcase_api_endpoints',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('testcase_id', sa.Integer(), nullable=False),
        sa.Column('api_endpoint_id', sa.Integer(), nullable=False),
        sa.Column('coverage_type', sa.String(30), nullable=True, server_default='functional'),
        sa.Column('confidence', sa.Integer(), nullable=True, server_default='100'),
        sa.Column('evidence', sa.Text(), nullable=True, server_default=''),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['testcase_id'], ['testcases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['api_endpoint_id'], ['api_endpoints.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'testcase_id', 'api_endpoint_id',
            name='uq_testcase_api_endpoint',
        ),
    )
    op.create_index('ix_testcase_api_endpoints_testcase_id', 'testcase_api_endpoints', ['testcase_id'])
    op.create_index('ix_testcase_api_endpoints_api_endpoint_id', 'testcase_api_endpoints', ['api_endpoint_id'])


def downgrade() -> None:
    op.drop_index('ix_testcase_api_endpoints_api_endpoint_id', table_name='testcase_api_endpoints')
    op.drop_index('ix_testcase_api_endpoints_testcase_id', table_name='testcase_api_endpoints')
    op.drop_table('testcase_api_endpoints')

    op.drop_index('ix_api_endpoints_fingerprint', table_name='api_endpoints')
    op.drop_index('ix_api_endpoints_tag', table_name='api_endpoints')
    op.drop_index('ix_api_endpoints_status', table_name='api_endpoints')
    op.drop_index('ix_api_endpoints_method_path', table_name='api_endpoints')
    op.drop_index('ix_api_endpoints_source_asset', table_name='api_endpoints')
    op.drop_index('ix_api_endpoints_project_sprint', table_name='api_endpoints')
    op.drop_table('api_endpoints')
