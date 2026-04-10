"""Curriculum Engine — 6 new tables + Task FK extension

Revision ID: 002
Revises: 001
Create Date: 2026-04-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── New enum types ──────────────────────────────────────────────────────
    op.execute("CREATE TYPE curriculumtype AS ENUM ('ALPHABET_ARABE', 'QAIDA_NOURANIA', 'MEDINE_T1', 'TAJWID', 'HIFZ_REVISION')")
    op.execute("CREATE TYPE unittype AS ENUM ('CHAPTER', 'MODULE', 'LESSON', 'LETTER', 'JUZ')")
    op.execute("CREATE TYPE itemtype AS ENUM ('LETTER_FORM', 'COMBINATION', 'RULE', 'VOCABULARY', 'GRAMMAR_POINT', 'SURAH_SEGMENT', 'EXAMPLE')")
    op.execute("CREATE TYPE enrollmentmode AS ENUM ('TEACHER_ASSIGNED', 'STUDENT_AUTONOMOUS')")
    op.execute("CREATE TYPE submissionstatus AS ENUM ('PENDING_REVIEW', 'APPROVED', 'NEEDS_IMPROVEMENT', 'REJECTED')")

    # ── Extend notificationtype enum (additive) ─────────────────────────────
    op.execute("ALTER TYPE notificationtype ADD VALUE IF NOT EXISTS 'SUBMISSION_RECEIVED'")
    op.execute("ALTER TYPE notificationtype ADD VALUE IF NOT EXISTS 'SUBMISSION_REVIEWED'")

    # ── curriculum_programs ─────────────────────────────────────────────────
    op.create_table(
        "curriculum_programs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("curriculum_type", sa.Enum("ALPHABET_ARABE", "QAIDA_NOURANIA", "MEDINE_T1", "TAJWID", "HIFZ_REVISION", name="curriculumtype"), unique=True, nullable=False),
        sa.Column("title_ar", sa.String(255), nullable=False),
        sa.Column("title_fr", sa.String(255), nullable=False),
        sa.Column("description_fr", sa.Text, nullable=True),
        sa.Column("total_units", sa.Integer, server_default="0"),
        sa.Column("cover_image_url", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("sort_order", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── curriculum_units ────────────────────────────────────────────────────
    op.create_table(
        "curriculum_units",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("curriculum_program_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_programs.id"), nullable=False),
        sa.Column("unit_type", sa.Enum("CHAPTER", "MODULE", "LESSON", "LETTER", "JUZ", name="unittype"), nullable=False),
        sa.Column("number", sa.Integer, nullable=False),
        sa.Column("title_ar", sa.String(255), nullable=False),
        sa.Column("title_fr", sa.String(255), nullable=True),
        sa.Column("description_fr", sa.Text, nullable=True),
        sa.Column("audio_url", sa.String(500), nullable=True),
        sa.Column("total_items", sa.Integer, server_default="0"),
        sa.Column("sort_order", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_curriculum_units_program_id", "curriculum_units", ["curriculum_program_id"])

    # ── curriculum_items ────────────────────────────────────────────────────
    op.create_table(
        "curriculum_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("curriculum_unit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_units.id"), nullable=False),
        sa.Column("item_type", sa.Enum("LETTER_FORM", "COMBINATION", "RULE", "VOCABULARY", "GRAMMAR_POINT", "SURAH_SEGMENT", "EXAMPLE", name="itemtype"), nullable=False),
        sa.Column("number", sa.Integer, nullable=False),
        sa.Column("title_ar", sa.String(500), nullable=False),
        sa.Column("title_fr", sa.String(500), nullable=True),
        sa.Column("content_ar", sa.Text, nullable=True),
        sa.Column("content_fr", sa.Text, nullable=True),
        sa.Column("transliteration", sa.String(500), nullable=True),
        sa.Column("audio_url", sa.String(500), nullable=True),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("surah_number", sa.Integer, nullable=True),
        sa.Column("verse_start", sa.Integer, nullable=True),
        sa.Column("verse_end", sa.Integer, nullable=True),
        sa.Column("letter_position", sa.String(20), nullable=True),
        sa.Column("metadata", postgresql.JSON, nullable=True),
        sa.Column("sort_order", sa.Integer, server_default="0"),
    )
    op.create_index("ix_curriculum_items_unit_id", "curriculum_items", ["curriculum_unit_id"])

    # ── student_enrollments ─────────────────────────────────────────────────
    op.create_table(
        "student_enrollments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("curriculum_program_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_programs.id"), nullable=False),
        sa.Column("teacher_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("mode", sa.Enum("TEACHER_ASSIGNED", "STUDENT_AUTONOMOUS", name="enrollmentmode"), server_default="STUDENT_AUTONOMOUS"),
        sa.Column("started_at", sa.Date, server_default=sa.func.current_date()),
        sa.Column("target_end_at", sa.Date, nullable=True),
        sa.Column("current_unit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_units.id"), nullable=True),
        sa.Column("current_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_items.id"), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("student_id", "curriculum_program_id", name="uq_enrollment_student_program"),
    )
    op.create_index("ix_student_enrollments_student_id", "student_enrollments", ["student_id"])

    # ── student_item_progress ───────────────────────────────────────────────
    op.create_table(
        "student_item_progress",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("enrollment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("student_enrollments.id"), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("curriculum_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_items.id"), nullable=False),
        sa.Column("is_completed", sa.Boolean, server_default="false"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("mastery_level", sa.Integer, nullable=True),
        sa.Column("attempt_count", sa.Integer, server_default="0"),
        sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("teacher_validated", sa.Boolean, server_default="false"),
        sa.Column("teacher_validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("enrollment_id", "curriculum_item_id", name="uq_item_progress"),
    )
    op.create_index("ix_student_item_progress_enrollment_id", "student_item_progress", ["enrollment_id"])
    op.create_index("ix_student_item_progress_student_id", "student_item_progress", ["student_id"])

    # ── student_submissions ─────────────────────────────────────────────────
    op.create_table(
        "student_submissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("teacher_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("enrollment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("student_enrollments.id"), nullable=False),
        sa.Column("curriculum_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("curriculum_items.id"), nullable=True),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tasks.id"), nullable=True),
        sa.Column("audio_url", sa.String(1000), nullable=True),
        sa.Column("text_content", sa.Text, nullable=True),
        sa.Column("status", sa.Enum("PENDING_REVIEW", "APPROVED", "NEEDS_IMPROVEMENT", "REJECTED", name="submissionstatus"), server_default="PENDING_REVIEW"),
        sa.Column("teacher_feedback", sa.Text, nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_student_submissions_student_id", "student_submissions", ["student_id"])
    op.create_index("ix_student_submissions_teacher_id", "student_submissions", ["teacher_id"])
    op.create_index("ix_student_submissions_status", "student_submissions", ["status"])

    # ── tasks: add curriculum_item_id FK (optional bridge) ─────────────────
    op.add_column("tasks", sa.Column(
        "curriculum_item_id",
        postgresql.UUID(as_uuid=True),
        sa.ForeignKey("curriculum_items.id", ondelete="SET NULL"),
        nullable=True,
    ))


def downgrade() -> None:
    op.drop_column("tasks", "curriculum_item_id")
    op.drop_table("student_submissions")
    op.drop_table("student_item_progress")
    op.drop_table("student_enrollments")
    op.drop_table("curriculum_items")
    op.drop_table("curriculum_units")
    op.drop_table("curriculum_programs")

    for enum_name in ["curriculumtype", "unittype", "itemtype", "enrollmentmode", "submissionstatus"]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
