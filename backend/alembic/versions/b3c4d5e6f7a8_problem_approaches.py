"""problem approaches (brute-force -> optimal ladder)

Revision ID: b3c4d5e6f7a8
Revises: c9d8e7f6a5b4
Create Date: 2026-10-19

Each problem can carry an ordered ladder of solution approaches, cheapest
first. Every entry records the idea, its complexity and — when a step-by-step
trace exists — the visualizer key that animates it. Problems without an
authored ladder keep the empty default, so nothing else changes.

Seed backfill happens in scripts/seed.py (app/seeds/data_approaches.py), not
here.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b3c4d5e6f7a8'
down_revision: Union[str, Sequence[str], None] = 'c9d8e7f6a5b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'problems',
        sa.Column(
            'approaches',
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column('problems', 'approaches')
