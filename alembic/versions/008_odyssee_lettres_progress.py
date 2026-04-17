"""L'Odyssée des Lettres — Per-student lesson progress table

Revision ID: 008
Revises: 007
Create Date: 2026-04-17

New tables:
- odyssee_lettres_progress: Per-student, per-lesson progress for the Arabic alphabet module
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "odyssee_lettres_progress",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("lesson_number", sa.Integer(), nullable=False, index=True),
        sa.Column("current_step", sa.Integer(), server_default="0"),
        sa.Column("ecoute_done", sa.Boolean(), server_default="false"),
        sa.Column("discovery_done", sa.Boolean(), server_default="false"),
        sa.Column("exercises_score", sa.Float(), nullable=True),
        sa.Column("mini_lecture_done", sa.Boolean(), server_default="false"),
        sa.Column("quiz_score", sa.Float(), nullable=True),
        sa.Column("stars", sa.Integer(), server_default="0"),
        sa.Column("xp_earned", sa.Integer(), server_default="0"),
        sa.Column("is_completed", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("student_id", "lesson_number", name="uq_odyssee_progress"),
    )


def downgrade() -> None:
    op.drop_table("odyssee_lettres_progress")
