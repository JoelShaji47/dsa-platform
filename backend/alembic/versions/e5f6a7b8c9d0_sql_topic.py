"""add SQL to the topic enum

Revision ID: e5f6a7b8c9d1
Revises: b8c9d0e1f2a3
Create Date: 2026-09-29

Adds the 'SQL' label to the ``topic`` Postgres enum for the standalone SQL
track. DSA topics and rows are untouched. Postgres cannot drop enum labels,
so downgrade only removes SQL problem rows and leaves the label in place.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e5f6a7b8c9d1'
down_revision: Union[str, Sequence[str], None] = 'b8c9d0e1f2a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(sa.text("ALTER TYPE topic ADD VALUE 'SQL'"))


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM problems WHERE topic = 'SQL'"))
