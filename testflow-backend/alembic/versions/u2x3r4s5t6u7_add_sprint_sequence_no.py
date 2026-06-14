"""add sprint sequence_no

Revision ID: u2x3r4s5t6u7
Revises: q8k1p2m3n4o5
Create Date: 2026-06-14
"""
import re
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'u2x3r4s5t6u7'
down_revision = 'q8k1p2m3n4o5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('sprints', sa.Column('sequence_no', sa.Integer(), nullable=True))
    op.create_index('ix_sprints_sequence_no', 'sprints', ['sequence_no'])
    # 回填：sprint_all -> 999999（排末尾）；名称含 sprintN -> N；其余保持 null（排末尾）
    bind = op.get_bind()
    num_re = re.compile(r"sprint[\s\-_]*0*(\d+)", re.IGNORECASE)
    rows = bind.execute(sa.text("SELECT id, name, is_all FROM sprints")).fetchall()
    for row in rows:
        seq = None
        if row.is_all:
            seq = 999999
        elif row.name:
            m = num_re.search(row.name)
            if m:
                seq = int(m.group(1))
        bind.execute(
            sa.text("UPDATE sprints SET sequence_no = :seq WHERE id = :id"),
            {"seq": seq, "id": row.id},
        )


def downgrade() -> None:
    op.drop_index('ix_sprints_sequence_no', table_name='sprints')
    op.drop_column('sprints', 'sequence_no')
