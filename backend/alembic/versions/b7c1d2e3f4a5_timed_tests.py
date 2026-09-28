"""timed test sessions

Revision ID: b7c1d2e3f4a5
Revises: f1a2b3c4d5e6
Create Date: 2026-09-28
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b7c1d2e3f4a5'
down_revision: Union[str, Sequence[str], None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TEST_STATUS_VALUES = ('IN_PROGRESS', 'SUBMITTED', 'EXPIRED', 'ABANDONED')

# create_type=False everywhere the type is referenced as a column: the type is
# created once, explicitly, at the top of upgrade(). Reusing the same ENUM
# object for both the explicit create and the column makes create_table emit a
# second CREATE TYPE in the same transaction.
test_status = postgresql.ENUM(
    *TEST_STATUS_VALUES, name='test_status', create_type=False
)
difficulty_enum = postgresql.ENUM(
    'EASY', 'MEDIUM', 'HARD', name='difficulty', create_type=False
)
topic_enum = postgresql.ENUM(
    'ARRAY', 'STRING', 'LINKED_LIST', 'STACK', 'QUEUE', 'TREE', 'GRAPH', 'DP',
    name='topic', create_type=False,
)
submission_status_enum = postgresql.ENUM(
    'ACCEPTED', 'WRONG_ANSWER', 'TLE', 'RUNTIME_ERROR', 'COMPILATION_ERROR',
    name='submission_status', create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    postgresql.ENUM(*TEST_STATUS_VALUES, name='test_status').create(
        bind, checkfirst=True
    )

    op.create_table(
        'test_sessions',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('status', test_status, server_default=sa.text("'IN_PROGRESS'::test_status"), nullable=False),
        sa.Column('topics', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column('assigned_topics', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column('duration_seconds', sa.Integer(), server_default=sa.text('3600'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deadline_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('time_taken_seconds', sa.Integer(), nullable=True),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('passed_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_test_sessions_user_id_users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_test_sessions')),
    )
    op.create_index('ix_test_sessions_user_status', 'test_sessions', ['user_id', 'status'], unique=False)

    op.create_table(
        'test_problems',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('session_id', sa.UUID(), nullable=False),
        sa.Column('problem_id', sa.UUID(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('difficulty', difficulty_enum, nullable=False),
        sa.Column('category', topic_enum, nullable=False),
        sa.Column('code', sa.Text(), nullable=True),
        sa.Column('language', sa.String(length=20), nullable=True),
        sa.Column('attempts', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('status', submission_status_enum, nullable=True),
        sa.Column('passed', sa.Boolean(), nullable=True),
        sa.Column('runtime_ms', sa.Float(), nullable=True),
        sa.Column('memory_kb', sa.Float(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], name=op.f('fk_test_problems_problem_id_problems'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['test_sessions.id'], name=op.f('fk_test_problems_session_id_test_sessions'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_test_problems')),
        sa.UniqueConstraint('session_id', 'position', name='uq_test_problem_position'),
        sa.UniqueConstraint('session_id', 'difficulty', name='uq_test_problem_difficulty'),
        sa.UniqueConstraint('session_id', 'problem_id', name='uq_test_problem_problem'),
    )
    op.create_index('ix_test_problems_session_id', 'test_problems', ['session_id'], unique=False)

    op.add_column(
        'submissions',
        sa.Column('test_session_id', sa.UUID(), nullable=True),
    )
    op.add_column(
        'submissions',
        sa.Column('test_problem_id', sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        'fk_submissions_test_session_id_test_sessions',
        'submissions', 'test_sessions',
        ['test_session_id'], ['id'],
        ondelete='CASCADE',
    )
    op.create_foreign_key(
        'fk_submissions_test_problem_id_test_problems',
        'submissions', 'test_problems',
        ['test_problem_id'], ['id'],
        ondelete='CASCADE',
    )
    op.create_index('ix_submissions_test_session_id', 'submissions', ['test_session_id'], unique=False)
    op.create_index('ix_submissions_test_problem_id', 'submissions', ['test_problem_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_submissions_test_problem_id', table_name='submissions')
    op.drop_index('ix_submissions_test_session_id', table_name='submissions')
    op.drop_constraint('fk_submissions_test_problem_id_test_problems', 'submissions', type_='foreignkey')
    op.drop_constraint('fk_submissions_test_session_id_test_sessions', 'submissions', type_='foreignkey')
    op.drop_column('submissions', 'test_problem_id')
    op.drop_column('submissions', 'test_session_id')

    op.drop_index('ix_test_problems_session_id', table_name='test_problems')
    op.drop_table('test_problems')

    op.drop_index('ix_test_sessions_user_status', table_name='test_sessions')
    op.drop_table('test_sessions')

    bind = op.get_bind()
    postgresql.ENUM(name='test_status').drop(bind, checkfirst=True)