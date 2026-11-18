"""Explicit recommendation feedback: clicks and dismissals

Revision ID: c5d6e7f8a9b0
Revises: b4c5d6e7f8a9
Create Date: 2026-11-18

Records what the learner did with an *exposed* recommendation. Until now the
only signal was ``rendered``, which says the card existed, not whether it was
useful. ``clicked_at`` / ``dismissed_at`` are deliberately nullable and are
written at most once per impression (first action wins), so downstream
analysis never has to resolve conflicting feedback.

These columns are NOT ranking features: they are observed after the decision
being modelled, so using them as inputs would leak the label back into the
ranker. They feed labels/analytics instead.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c5d6e7f8a9b0'
down_revision: Union[str, Sequence[str], None] = 'b4c5d6e7f8a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'recommendation_impressions',
        sa.Column('clicked_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        'recommendation_impressions',
        sa.Column('dismissed_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('recommendation_impressions', 'dismissed_at')
    op.drop_column('recommendation_impressions', 'clicked_at')
