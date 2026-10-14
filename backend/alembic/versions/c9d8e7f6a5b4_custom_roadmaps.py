"""custom roadmaps: builder + friend join + weekly rate limit

Revision ID: c9d8e7f6a5b4
Revises: a1b2c3d4e5f6
Create Date: 2026-10-14
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c9d8e7f6a5b4'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'custom_roadmaps',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('owner_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(200), server_default='My roadmap', nullable=False),
        sa.Column('kind', sa.String(30), server_default='dsa_build', nullable=False),
        sa.Column('level', sa.String(30), server_default='basics', nullable=False),
        sa.Column('goal', sa.String(30), server_default='fundamentals', nullable=False),
        sa.Column('company', sa.String(100), nullable=True),
        sa.Column('mins_per_day', sa.Integer(), server_default='60', nullable=False),
        sa.Column('total_days', sa.Integer(), server_default='21', nullable=False),
        sa.Column('target_count', sa.Integer(), nullable=True),
        sa.Column('share_code', sa.CHAR(6), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('share_code'),
    )
    op.create_index('ix_custom_roadmaps_share_code', 'custom_roadmaps', ['share_code'], unique=True)
    op.create_index('ix_custom_roadmaps_owner_id', 'custom_roadmaps', ['owner_id'], unique=False)

    op.create_table(
        'custom_roadmap_steps',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('roadmap_id', sa.UUID(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('problem_slug', sa.String(220), nullable=True),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('kind', sa.String(20), server_default='problem', nullable=False),
        sa.Column('pattern_key', sa.String(60), nullable=True),
        sa.Column('difficulty', sa.String(20), nullable=True),
        sa.Column('est_mins', sa.Integer(), server_default='45', nullable=False),
        sa.Column('day_index', sa.Integer(), server_default='1', nullable=False),
        sa.Column('meta', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.ForeignKeyConstraint(['roadmap_id'], ['custom_roadmaps.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('roadmap_id', 'position', name='uq_custom_step_position'),
    )
    op.create_index('ix_custom_roadmap_steps_roadmap_id', 'custom_roadmap_steps', ['roadmap_id'], unique=False)
    op.create_index('ix_custom_steps_roadmap_day', 'custom_roadmap_steps', ['roadmap_id', 'day_index'], unique=False)

    op.create_table(
        'custom_roadmap_members',
        sa.Column('roadmap_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['roadmap_id'], ['custom_roadmaps.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('roadmap_id', 'user_id'),
    )

    op.create_table(
        'custom_roadmap_ticks',
        sa.Column('step_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('done_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['step_id'], ['custom_roadmap_steps.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('step_id', 'user_id'),
    )

    op.create_table(
        'custom_roadmap_generations',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_custom_roadmap_generations_user_id', 'custom_roadmap_generations', ['user_id'], unique=False)
    op.create_index('ix_custom_generations_user_created', 'custom_roadmap_generations', ['user_id', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_table('custom_roadmap_generations')
    op.drop_table('custom_roadmap_ticks')
    op.drop_table('custom_roadmap_members')
    op.drop_table('custom_roadmap_steps')
    op.drop_table('custom_roadmaps')
