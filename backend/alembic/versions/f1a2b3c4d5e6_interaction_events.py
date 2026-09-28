"""interaction events log (recommender telemetry)

Revision ID: f1a2b3c4d5e6
Revises: 9d4e5f6a7b8c
Create Date: 2026-09-15
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = '9d4e5f6a7b8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'interaction_events',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('problem_id', sa.UUID(), nullable=False),
        sa.Column('event', sa.String(length=30), nullable=False),
        sa.Column('meta', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], name=op.f('fk_interaction_events_problem_id_problems'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_interaction_events_user_id_users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_interaction_events')),
    )
    op.create_index('ix_events_user_problem', 'interaction_events', ['user_id', 'problem_id'], unique=False)
    op.create_index('ix_events_created', 'interaction_events', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_events_created', table_name='interaction_events')
    op.drop_index('ix_events_user_problem', table_name='interaction_events')
    op.drop_table('interaction_events')
