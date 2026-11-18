"""recommendation telemetry: impressions + solve sessions

Revision ID: a1b2c3d4e5f6
Revises: b3c4d5e6f7a8
Create Date: 2026-10-14
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'b3c4d5e6f7a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'recommendation_opportunities',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('model_version', sa.String(length=60), nullable=False),
        sa.Column('feature_schema_version', sa.Integer(), server_default=sa.text('2'), nullable=False),
        sa.Column('candidate_count', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_recommendation_opportunities_user_id_users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_recommendation_opportunities')),
    )
    op.create_index('ix_rec_opps_user_created', 'recommendation_opportunities', ['user_id', 'created_at'], unique=False)

    op.create_table(
        'recommendation_impressions',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('opportunity_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('problem_id', sa.UUID(), nullable=False),
        sa.Column('rank', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(length=30), server_default=sa.text("'roadmap'"), nullable=False),
        sa.Column('model_version', sa.String(length=60), nullable=False),
        sa.Column('feature_schema_version', sa.Integer(), server_default=sa.text('2'), nullable=False),
        sa.Column('rendered', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['opportunity_id'], ['recommendation_opportunities.id'], name=op.f('fk_recommendation_impressions_opportunity_id_recommendation_opportunities'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], name=op.f('fk_recommendation_impressions_problem_id_problems'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_recommendation_impressions_user_id_users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_recommendation_impressions')),
        sa.UniqueConstraint('opportunity_id', 'problem_id', name='uq_impression_opp_problem'),
    )
    op.create_index('ix_impressions_user_created', 'recommendation_impressions', ['user_id', 'created_at'], unique=False)
    op.create_index('ix_impressions_problem', 'recommendation_impressions', ['problem_id'], unique=False)
    op.create_index('ix_impressions_opportunity', 'recommendation_impressions', ['opportunity_id'], unique=False)

    op.create_table(
        'solve_sessions',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('client_session_id', sa.String(length=60), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('problem_id', sa.UUID(), nullable=False),
        sa.Column('opportunity_id', sa.UUID(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_heartbeat_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('heartbeat_count', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('active_seconds', sa.Float(), server_default=sa.text('0'), nullable=False),
        sa.Column('attempt_count', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('hint_count', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('run_count', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('review_count', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('editorial_revealed', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('status', sa.String(length=20), server_default=sa.text("'active'"), nullable=False),
        sa.Column('first_accepted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('claimed_time_complexity', sa.String(length=20), nullable=True),
        sa.Column('claimed_space_complexity', sa.String(length=20), nullable=True),
        sa.Column('verified_time_complexity', sa.String(length=20), nullable=True),
        sa.Column('verified_space_complexity', sa.String(length=20), nullable=True),
        sa.Column('meta', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['opportunity_id'], ['recommendation_opportunities.id'], name=op.f('fk_solve_sessions_opportunity_id_recommendation_opportunities'), ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], name=op.f('fk_solve_sessions_problem_id_problems'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_solve_sessions_user_id_users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_solve_sessions')),
        sa.UniqueConstraint('user_id', 'client_session_id', name='uq_session_user_client'),
    )
    op.create_index('ix_sessions_user_problem', 'solve_sessions', ['user_id', 'problem_id'], unique=False)
    op.create_index('ix_sessions_created', 'solve_sessions', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_sessions_created', table_name='solve_sessions')
    op.drop_index('ix_sessions_user_problem', table_name='solve_sessions')
    op.drop_table('solve_sessions')
    op.drop_index('ix_impressions_opportunity', table_name='recommendation_impressions')
    op.drop_index('ix_impressions_problem', table_name='recommendation_impressions')
    op.drop_index('ix_impressions_user_created', table_name='recommendation_impressions')
    op.drop_table('recommendation_impressions')
    op.drop_index('ix_rec_opps_user_created', table_name='recommendation_opportunities')
    op.drop_table('recommendation_opportunities')
