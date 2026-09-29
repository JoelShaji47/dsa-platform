"""Merge timed-tests and function-mode heads.

Revision ID: d4e5f6a7b8c9
Revises: c8d2e3f4a5b6, c3d4e5f6a7b8
"""

from typing import Sequence, Union


revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, Sequence[str], None] = ('c8d2e3f4a5b6', 'c3d4e5f6a7b8')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
