"""custom test questions: allow repeated difficulties

Revision ID: f7a8b9c0d1e2
Revises: e5f6a7b8c9d1
Create Date: 2026-10-14

Custom timed tests let users pick 1-6 questions with any difficulty mix
(e.g. EASY+EASY+MEDIUM), so the one-difficulty-per-session unique
constraint has to go. Position + problem uniqueness stays.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'f7a8b9c0d1e2'
down_revision: Union[str, Sequence[str], None] = 'e5f6a7b8c9d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        'uq_test_problem_difficulty', 'test_problems', type_='unique'
    )


def downgrade() -> None:
    op.create_unique_constraint(
        'uq_test_problem_difficulty',
        'test_problems',
        ['session_id', 'difficulty'],
    )
