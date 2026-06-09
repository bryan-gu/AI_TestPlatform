"""expand feature points testcases and coverage

Revision ID: k2e5j6g7h8i9
Revises: j1d4i5f6g7h8
Create Date: 2026-06-09 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'k2e5j6g7h8i9'
down_revision = 'j1d4i5f6g7h8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('feature_points', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('feature_points', sa.Column('entry_path', sa.Text(), nullable=True))
    op.add_column('feature_points', sa.Column('interaction_elements', sa.Text(), nullable=True))
    op.add_column('feature_points', sa.Column('business_rules', sa.Text(), nullable=True))
    op.add_column('feature_points', sa.Column('priority', sa.String(10), nullable=True))
    op.add_column('feature_points', sa.Column('source_type', sa.String(30), nullable=True))
    op.add_column('feature_points', sa.Column('status', sa.String(30), nullable=True))
    op.add_column('feature_points', sa.Column('version', sa.String(40), nullable=True))
    op.add_column('feature_points', sa.Column('fingerprint', sa.String(64), nullable=True))
    op.add_column('feature_points', sa.Column('raw_data', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('feature_points', sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True))
    op.execute("""
        UPDATE feature_points
        SET description = COALESCE(description, ''),
            entry_path = COALESCE(entry_path, ''),
            interaction_elements = COALESCE(interaction_elements, ''),
            business_rules = COALESCE(business_rules, ''),
            priority = COALESCE(priority, '中'),
            source_type = COALESCE(source_type, 'manual'),
            status = COALESCE(status, 'active'),
            version = COALESCE(version, 'v1.0'),
            fingerprint = COALESCE(fingerprint, ''),
            raw_data = COALESCE(raw_data, '{}'::json)
    """)

    op.add_column('testcases', sa.Column('sprint_id', sa.Integer(), nullable=True))
    op.add_column('testcases', sa.Column('case_type', sa.String(30), nullable=True))
    op.add_column('testcases', sa.Column('automation_status', sa.String(30), nullable=True))
    op.add_column('testcases', sa.Column('automation_path', sa.String(500), nullable=True))
    op.add_column('testcases', sa.Column('selector_path', sa.String(500), nullable=True))
    op.add_column('testcases', sa.Column('source', sa.String(30), nullable=True))
    op.add_column('testcases', sa.Column('version', sa.String(40), nullable=True))
    op.add_column('testcases', sa.Column('fingerprint', sa.String(64), nullable=True))
    op.add_column('testcases', sa.Column('raw_data', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.create_foreign_key('fk_testcases_sprint_id', 'testcases', 'sprints', ['sprint_id'], ['id'])
    op.execute("""
        UPDATE testcases
        SET case_type = COALESCE(case_type, 'ui'),
            automation_status = COALESCE(automation_status, 'not_generated'),
            automation_path = COALESCE(automation_path, ''),
            selector_path = COALESCE(selector_path, ''),
            source = COALESCE(source, 'manual'),
            version = COALESCE(version, 'v1.0'),
            fingerprint = COALESCE(fingerprint, ''),
            raw_data = COALESCE(raw_data, '{}'::json)
    """)

    op.create_table(
        'feature_point_testcases',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('feature_point_id', sa.Integer(), nullable=False),
        sa.Column('testcase_id', sa.Integer(), nullable=False),
        sa.Column('coverage_type', sa.String(30), nullable=True),
        sa.Column('confidence', sa.Integer(), nullable=True),
        sa.Column('evidence', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['feature_point_id'], ['feature_points.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['testcase_id'], ['testcases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_feature_point_testcases_feature_point_id', 'feature_point_testcases', ['feature_point_id'])
    op.create_index('ix_feature_point_testcases_testcase_id', 'feature_point_testcases', ['testcase_id'])


def downgrade() -> None:
    op.drop_index('ix_feature_point_testcases_testcase_id', table_name='feature_point_testcases')
    op.drop_index('ix_feature_point_testcases_feature_point_id', table_name='feature_point_testcases')
    op.drop_table('feature_point_testcases')

    op.drop_constraint('fk_testcases_sprint_id', 'testcases', type_='foreignkey')
    op.drop_column('testcases', 'raw_data')
    op.drop_column('testcases', 'fingerprint')
    op.drop_column('testcases', 'version')
    op.drop_column('testcases', 'source')
    op.drop_column('testcases', 'selector_path')
    op.drop_column('testcases', 'automation_path')
    op.drop_column('testcases', 'automation_status')
    op.drop_column('testcases', 'case_type')
    op.drop_column('testcases', 'sprint_id')

    op.drop_column('feature_points', 'updated_at')
    op.drop_column('feature_points', 'raw_data')
    op.drop_column('feature_points', 'fingerprint')
    op.drop_column('feature_points', 'version')
    op.drop_column('feature_points', 'status')
    op.drop_column('feature_points', 'source_type')
    op.drop_column('feature_points', 'priority')
    op.drop_column('feature_points', 'business_rules')
    op.drop_column('feature_points', 'interaction_elements')
    op.drop_column('feature_points', 'entry_path')
    op.drop_column('feature_points', 'description')
