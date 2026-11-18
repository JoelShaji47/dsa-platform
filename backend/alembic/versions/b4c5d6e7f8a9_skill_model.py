"""Layer 1 student model: per-user skill estimates + problem difficulty

Revision ID: b4c5d6e7f8a9
Revises: a1b2c3d4e5f6
Create Date: 2026-11-18

Adds the durable state for the Elo/IRT student model:

``skill_estimates``      one row per (user, pattern): ability logit theta and
                         the observation count n behind it.
``problems.difficulty_b`` learned problem difficulty logit (NULL until the
                         first graded submission, in which case the difficulty
                         band prior applies).
``problems.difficulty_n`` observations behind difficulty_b.

No backfill here: ``scripts/refit_skill_model.py`` replays the submission log
once, which is the only correct way to populate historical estimates.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b4c5d6e7f8a9'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'skill_estimates',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('pattern_key', sa.String(length=60), nullable=False),
        sa.Column('theta', sa.Float(), server_default=sa.text('0'), nullable=False),
        sa.Column('n', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(
            ['user_id'], ['users.id'],
            name=op.f('fk_skill_estimates_user_id_users'), ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_skill_estimates')),
        sa.UniqueConstraint('user_id', 'pattern_key', name='uq_skill_estimates_user_pattern'),
    )
    op.create_index('ix_skill_estimates_user', 'skill_estimates', ['user_id'], unique=False)
    op.create_index('ix_skill_estimates_pattern', 'skill_estimates', ['pattern_key'], unique=False)

    op.add_column('problems', sa.Column('difficulty_b', sa.Float(), nullable=True))
    op.add_column(
        'problems',
        sa.Column('difficulty_n', sa.Integer(), server_default=sa.text('0'), nullable=False),
    )


def downgrade() -> None:
    op.drop_column('problems', 'difficulty_n')
    op.drop_column('problems', 'difficulty_b')
    op.drop_index('ix_skill_estimates_pattern', table_name='skill_estimates')
    op.drop_index('ix_skill_estimates_user', table_name='skill_estimates')
    op.drop_table('skill_estimates')
