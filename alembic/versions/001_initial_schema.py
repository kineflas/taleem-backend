"""Initial schema — all tables

Revision ID: 001
Revises:
Create Date: 2026-04-08
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── users ──────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("TEACHER", "STUDENT", name="userrole"), nullable=False),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("locale", sa.String(10), server_default="ar"),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("is_child_profile", sa.Boolean, server_default="false"),
        sa.Column("parent_pin_hash", sa.String(255), nullable=True),
        sa.Column("fcm_token", sa.String(500), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # ── teacher_student_links ───────────────────────────────────────────────
    op.create_table(
        "teacher_student_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("teacher_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("linked_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("joker_quota_override", sa.Integer, nullable=True),
        sa.Column("invitation_code", sa.String(10), nullable=True),
        sa.Column("invitation_expires_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_teacher_student_links_invitation_code", "teacher_student_links", ["invitation_code"])

    # ── programs ───────────────────────────────────────────────────────────
    op.create_table(
        "programs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("teacher_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("pillar", sa.Enum("QURAN", "ARABIC", "BOTH", name="pillartype"), nullable=False),
        sa.Column("status", sa.Enum("ACTIVE", "PAUSED", "COMPLETED", name="programstatus"), server_default="ACTIVE"),
        sa.Column("started_at", sa.Date, server_default=sa.func.current_date()),
        sa.Column("target_end_at", sa.Date, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── tasks ──────────────────────────────────────────────────────────────
    op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("program_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("programs.id"), nullable=False),
        sa.Column("teacher_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("pillar", sa.Enum("QURAN", "ARABIC", "BOTH", name="pillartype"), nullable=False),
        sa.Column("task_type", sa.Enum("MEMORIZATION", "REVISION", "READING", "GRAMMAR", "VOCABULARY", name="tasktype"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("surah_number", sa.Integer, nullable=True),
        sa.Column("surah_name", sa.String(100), nullable=True),
        sa.Column("verse_start", sa.Integer, nullable=True),
        sa.Column("verse_end", sa.Integer, nullable=True),
        sa.Column("book_ref", sa.Enum("MEDINA_T1", "MEDINA_T2", "MEDINA_T3", "NORANIA", "QAIDA_BAGHDADIYA", "OTHER", name="bookref"), nullable=True),
        sa.Column("chapter_number", sa.Integer, nullable=True),
        sa.Column("chapter_title", sa.String(255), nullable=True),
        sa.Column("page_start", sa.Integer, nullable=True),
        sa.Column("page_end", sa.Integer, nullable=True),
        sa.Column("custom_ref", sa.String(255), nullable=True),
        sa.Column("due_date", sa.Date, nullable=False),
        sa.Column("scheduled_date", sa.Date, nullable=True),
        sa.Column("repeat_type", sa.Enum("NONE", "DAILY", "WEEKLY", "CUSTOM", name="repeattype"), server_default="NONE"),
        sa.Column("repeat_days", postgresql.JSON, nullable=True),
        sa.Column("repeat_until", sa.Date, nullable=True),
        sa.Column("repeat_group_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.Enum("PENDING", "COMPLETED", "MISSED", "SKIPPED", name="taskstatus"), server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_tasks_student_id", "tasks", ["student_id"])
    op.create_index("ix_tasks_due_date", "tasks", ["due_date"])
    op.create_index("ix_tasks_status", "tasks", ["status"])
    op.create_index("ix_tasks_repeat_group_id", "tasks", ["repeat_group_id"])

    # ── task_completions ───────────────────────────────────────────────────
    op.create_table(
        "task_completions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tasks.id"), unique=True, nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("difficulty", sa.Integer, nullable=True),
        sa.Column("student_note", sa.Text, nullable=True),
        sa.Column("teacher_read", sa.Boolean, server_default="false"),
        sa.Column("parent_validated", sa.Boolean, server_default="false"),
        sa.Column("parent_validated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_task_completions_student_id", "task_completions", ["student_id"])

    # ── streaks ────────────────────────────────────────────────────────────
    op.create_table(
        "streaks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), unique=True, nullable=False),
        sa.Column("current_streak_days", sa.Integer, server_default="0"),
        sa.Column("longest_streak_days", sa.Integer, server_default="0"),
        sa.Column("last_activity_date", sa.Date, server_default=sa.func.current_date()),
        sa.Column("total_completed_tasks", sa.Integer, server_default="0"),
        sa.Column("jokers_total", sa.Integer, server_default="3"),
        sa.Column("jokers_used_this_month", sa.Integer, server_default="0"),
        sa.Column("jokers_reset_at", sa.Date, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── joker_usages ───────────────────────────────────────────────────────
    op.create_table(
        "joker_usages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("used_for_date", sa.Date, nullable=False),
        sa.Column("reason", sa.Enum("ILLNESS", "TRAVEL", "FAMILY", "OTHER", name="jokerreason"), nullable=False),
        sa.Column("note", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_joker_usages_student_id", "joker_usages", ["student_id"])

    # ── notifications ──────────────────────────────────────────────────────
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("recipient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("type", sa.Enum(
            "TASK_DUE", "TASK_MISSED", "STUDENT_FEEDBACK_HARD",
            "STREAK_AT_RISK", "PROGRAM_UPDATE", "JOKER_LOW",
            "NEW_TASK_ASSIGNED", "STREAK_BROKEN",
            name="notificationtype"
        ), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("related_task_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_read", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_notifications_recipient_id", "notifications", ["recipient_id"])

    # ── surahs ─────────────────────────────────────────────────────────────
    op.create_table(
        "surahs",
        sa.Column("surah_number", sa.Integer, primary_key=True),
        sa.Column("surah_name_ar", sa.String(100), nullable=False),
        sa.Column("surah_name_fr", sa.String(100), nullable=False),
        sa.Column("surah_name_en", sa.String(100), nullable=False),
        sa.Column("total_verses", sa.Integer, nullable=False),
        sa.Column("juz_number", sa.Integer, nullable=False),
        sa.Column("is_meccan", sa.Boolean, server_default="true"),
    )


def downgrade() -> None:
    op.drop_table("surahs")
    op.drop_table("notifications")
    op.drop_table("joker_usages")
    op.drop_table("streaks")
    op.drop_table("task_completions")
    op.drop_table("tasks")
    op.drop_table("programs")
    op.drop_table("teacher_student_links")
    op.drop_table("users")

    # Drop enum types
    for enum_name in ["userrole", "pillartype", "programstatus", "tasktype",
                      "taskstatus", "repeattype", "bookref", "jokerreason", "notificationtype"]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
