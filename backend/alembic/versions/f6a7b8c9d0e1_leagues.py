"""Weekly leagues (Duolingo-style tiers + cohorts + season history).

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f6a7b8c9d0e1'
down_revision: Union[str, Sequence[str], None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('league_tier', sa.Integer(), server_default=sa.text('0'), nullable=False),
    )
    op.create_table(
        'leagues',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('week_start', sa.Date(), nullable=False),
        sa.Column('tier', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_leagues')),
    )
    op.create_index('ix_leagues_week', 'leagues', ['week_start'], unique=False)
    op.create_table(
        'league_members',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('league_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('final_rank', sa.Integer(), nullable=True),
        sa.Column('final_xp', sa.Integer(), nullable=True),
        sa.Column('movement', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['league_id'], ['leagues.id'], name=op.f('fk_league_members_league_id_leagues'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_league_members_user_id_users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_league_members')),
        sa.UniqueConstraint('league_id', 'user_id', name='uq_league_member'),
    )
    op.create_index('ix_league_members_league', 'league_members', ['league_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_league_members_league', table_name='league_members')
    op.drop_table('league_members')
    op.drop_index('ix_leagues_week', table_name='leagues')
    op.drop_table('leagues')
    op.drop_column('users', 'league_tier')
