"""problem provenance (sources, pattern, companies, links)

Revision ID: 9d4e5f6a7b8c
Revises: 483e3cae9425
Create Date: 2026-09-15

Adds multi-source catalog support so the same library can merge the NeetCode
and Take-U-Forward curricula: which sheet(s) list a problem, which roadmap
pattern it belongs to, frequent companies, and editorial/video links.
Backfilling of existing rows happens in scripts/seed.py (sources default to
['neetcode'], pattern_key from the roadmap map), not here.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9d4e5f6a7b8c'
down_revision: Union[str, Sequence[str], None] = '483e3cae9425'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'problems',
        sa.Column(
            'sources',
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column(
        'problems', sa.Column('pattern_key', sa.String(length=60), nullable=True)
    )
    op.create_index(
        op.f('ix_problems_pattern_key'), 'problems', ['pattern_key'], unique=False
    )
    op.add_column(
        'problems',
        sa.Column(
            'companies',
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column(
        'problems', sa.Column('editorial_url', sa.String(length=500), nullable=True)
    )
    op.add_column(
        'problems', sa.Column('video_url', sa.String(length=500), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('problems', 'video_url')
    op.drop_column('problems', 'editorial_url')
    op.drop_column('problems', 'companies')
    op.drop_index(op.f('ix_problems_pattern_key'), table_name='problems')
    op.drop_column('problems', 'pattern_key')
    op.drop_column('problems', 'sources')
