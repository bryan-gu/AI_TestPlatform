"""add knowledge assets table

Revision ID: l3f6k7h8i9j0
Revises: k2e5j6g7h8i9
Create Date: 2026-06-10 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'l3f6k7h8i9j0'
down_revision = 'k2e5j6g7h8i9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'knowledge_assets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('sprint_id', sa.Integer(), nullable=True),
        sa.Column('document_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('asset_type', sa.String(40), nullable=False, server_default='other'),
        sa.Column('source_kind', sa.String(40), nullable=True, server_default='uploaded'),
        sa.Column('file_path', sa.String(500), nullable=True, server_default=''),
        sa.Column('file_type', sa.String(40), nullable=True, server_default=''),
        sa.Column('file_size', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('module_id', sa.Integer(), nullable=True),
        sa.Column('version', sa.String(40), nullable=True, server_default='v1.0'),
        sa.Column('status', sa.String(30), nullable=True, server_default='active'),
        sa.Column('parse_status', sa.String(30), nullable=True, server_default='pending'),
        sa.Column('content_hash', sa.String(64), nullable=True, server_default=''),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['sprint_id'], ['sprints.id']),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_knowledge_assets_project_id', 'knowledge_assets', ['project_id'])
    op.create_index('ix_knowledge_assets_sprint_id', 'knowledge_assets', ['sprint_id'])
    op.create_index('ix_knowledge_assets_document_id', 'knowledge_assets', ['document_id'])
    op.create_index('ix_knowledge_assets_asset_type', 'knowledge_assets', ['asset_type'])
    op.create_index('ix_knowledge_assets_status', 'knowledge_assets', ['status'])

    op.execute("""
        INSERT INTO knowledge_assets (
            project_id, sprint_id, document_id, name, asset_type, source_kind,
            file_path, file_type, file_size, module_id, version, status,
            parse_status, content_hash, metadata, created_by, created_at, updated_at
        )
        SELECT
            s.project_id,
            d.sprint_id,
            d.id,
            d.name,
            CASE
                WHEN d.ai_status = 'AI生成' AND d.file_type = 'Markdown' AND d.name LIKE '%功能点%' THEN 'feature_spec'
                WHEN d.ai_status = 'AI生成' AND d.file_type = 'JSON' THEN 'test_case_json'
                WHEN d.ai_status = 'AI生成' AND d.file_type = 'Excel' THEN 'test_case_excel'
                WHEN d.file_type = 'Excel' THEN 'test_case_excel'
                WHEN d.file_type = 'JSON' AND lower(d.name) LIKE '%openapi%' THEN 'api_doc_openapi'
                WHEN d.file_type = 'JSON' THEN 'test_case_json'
                WHEN d.name LIKE '%接口%' THEN 'api_doc_md'
                WHEN d.name LIKE '%会议%' THEN 'meeting_note'
                WHEN d.file_type IN ('PDF', 'Word', 'Markdown') THEN 'requirement_doc'
                ELSE 'other'
            END,
            CASE WHEN d.ai_status = 'AI生成' THEN 'ai_generated' ELSE 'uploaded' END,
            COALESCE(d.file_path, ''),
            COALESCE(d.file_type, ''),
            COALESCE(d.file_size, 0),
            NULL,
            COALESCE(d.version, 'v1.0'),
            'active',
            COALESCE(d.parse_status, 'pending'),
            '',
            '{}'::json,
            d.uploader_id,
            d.created_at,
            now()
        FROM documents d
        LEFT JOIN sprints s ON s.id = d.sprint_id
    """)


def downgrade() -> None:
    op.drop_index('ix_knowledge_assets_status', table_name='knowledge_assets')
    op.drop_index('ix_knowledge_assets_asset_type', table_name='knowledge_assets')
    op.drop_index('ix_knowledge_assets_document_id', table_name='knowledge_assets')
    op.drop_index('ix_knowledge_assets_sprint_id', table_name='knowledge_assets')
    op.drop_index('ix_knowledge_assets_project_id', table_name='knowledge_assets')
    op.drop_table('knowledge_assets')
