"""add source_asset_id to feature_points and testcases

Revision ID: q8k1p2m3n4o5
Revises: p7j0o1l2m3n4
Create Date: 2026-06-13 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'q8k1p2m3n4o5'
down_revision = 'p7j0o1l2m3n4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # feature_points.source_asset_id
    op.add_column('feature_points', sa.Column('source_asset_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_feature_points_source_asset_id',
        'feature_points', 'knowledge_assets',
        ['source_asset_id'], ['id'],
    )
    op.create_index('ix_feature_points_source_asset_id', 'feature_points', ['source_asset_id'])

    # testcases.source_asset_id
    op.add_column('testcases', sa.Column('source_asset_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_testcases_source_asset_id',
        'testcases', 'knowledge_assets',
        ['source_asset_id'], ['id'],
    )
    op.create_index('ix_testcases_source_asset_id', 'testcases', ['source_asset_id'])

    # 回填 FeaturePoint.source_asset_id：通过 source_doc_id -> knowledge_assets.document_id
    op.execute("""
        UPDATE feature_points AS fp
        SET source_asset_id = ka.id
        FROM knowledge_assets AS ka
        WHERE fp.source_asset_id IS NULL
          AND fp.source_doc_id IS NOT NULL
          AND fp.source_doc_id = ka.document_id
    """)
    # TestCase 历史数据来源不可靠，保守保持 NULL，由后续流水线写入


def downgrade() -> None:
    op.drop_index('ix_testcases_source_asset_id', table_name='testcases')
    op.drop_constraint('fk_testcases_source_asset_id', 'testcases', type_='foreignkey')
    op.drop_column('testcases', 'source_asset_id')

    op.drop_index('ix_feature_points_source_asset_id', table_name='feature_points')
    op.drop_constraint('fk_feature_points_source_asset_id', 'feature_points', type_='foreignkey')
    op.drop_column('feature_points', 'source_asset_id')
