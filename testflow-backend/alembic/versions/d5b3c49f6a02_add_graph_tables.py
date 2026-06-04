"""add graph tables

Revision ID: d5b3c49f6a02
Revises: c4a2b38e5f01
Create Date: 2026-06-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5b3c49f6a02'
down_revision: Union[str, None] = 'c4a2b38e5f01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # graphs
    op.create_table(
        'graphs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('sprint_id', sa.Integer(), nullable=True),
        sa.Column('node_count', sa.Integer(), server_default='0', nullable=True),
        sa.Column('edge_count', sa.Integer(), server_default='0', nullable=True),
        sa.Column('status', sa.String(length=20), server_default='最新', nullable=True),
        sa.Column('generated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['sprint_id'], ['sprints.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )

    # graph_nodes
    op.create_table(
        'graph_nodes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('graph_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('node_type', sa.String(length=20), nullable=False),
        sa.Column('properties', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['graph_id'], ['graphs.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )

    # graph_edges
    op.create_table(
        'graph_edges',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('graph_id', sa.Integer(), nullable=False),
        sa.Column('source_node_id', sa.Integer(), nullable=False),
        sa.Column('target_node_id', sa.Integer(), nullable=False),
        sa.Column('relation_type', sa.String(length=30), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['graph_id'], ['graphs.id'], ),
        sa.ForeignKeyConstraint(['source_node_id'], ['graph_nodes.id'], ),
        sa.ForeignKeyConstraint(['target_node_id'], ['graph_nodes.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('graph_edges')
    op.drop_table('graph_nodes')
    op.drop_table('graphs')
