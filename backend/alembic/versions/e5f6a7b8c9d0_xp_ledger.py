"""XP ledger + streak-freeze inventory (leagues/shop foundation).

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, Sequence[str], None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('streak_freezes', sa.Integer(), server_default=sa.text('0'), nullable=False),
    )
    op.create_table(
        'xp_events',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(length=30), nullable=False),
        sa.Column('problem_id', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], name=op.f('fk_xp_events_problem_id_problems'), ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_xp_events_user_id_users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_xp_events')),
    )
    op.create_index('ix_xp_events_user_created', 'xp_events', ['user_id', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_xp_events_user_created', table_name='xp_events')
    op.drop_table('xp_events')
    op.drop_column('users', 'streak_freezes')
