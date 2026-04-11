"""Hifz Master — Quranic memorization gamification with XP + badges

Revision ID: 005
Revises: 004
Create Date: 2026-04-10

Creates 5 tables + 5 enums:
- hifz_goals: Memorization goals (surah-level)
- verse_progress: Per-verse mastery tracking (Leitner-like)
- hifz_sessions: Memorization practice sessions
- student_xp: XP + level progression
- student_badges: Achievement badges
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Pre-define enum types with create_type=False
_versemastery = postgresql.ENUM(
    "RED", "ORANGE", "GREEN",
    name="versemastery", create_type=False
)
_goalmode = postgresql.ENUM(
    "QUANTITATIVE", "TEMPORAL",
    name="goalmode", create_type=False
)
_badgetype = postgresql.ENUM(
    "HIZB", "SURAH_COMPLETE", "STREAK_7", "STREAK_30", "STREAK_100",
    "LEVEL_UP", "FIRST_JUZ", "RECITER_10",
    name="badgetype", create_type=False
)
_studentlevel = postgresql.ENUM(
    "DEBUTANT", "APPRENTI", "HAFIZ_EN_HERBE", "HAFIZ_CONFIRME", "HAFIZ_EXPERT",
    name="studentlevel", create_type=False
)

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Create enum types ───────────────────────────────────────────────────
    op.execute("CREATE TYPE versemastery AS ENUM ('RED', 'ORANGE', 'GREEN')")
    op.execute("CREATE TYPE goalmode AS ENUM ('QUANTITATIVE', 'TEMPORAL')")
    op.execute("CREATE TYPE badgetype AS ENUM ('HIZB', 'SURAH_COMPLETE', 'STREAK_7', 'STREAK_30', 'STREAK_100', 'LEVEL_UP', 'FIRST_JUZ', 'RECITER_10')")
    op.execute("CREATE TYPE studentlevel AS ENUM ('DEBUTANT', 'APPRENTI', 'HAFIZ_EN_HERBE', 'HAFIZ_CONFIRME', 'HAFIZ_EXPERT')")

    # ── 1. hifz_goals ──────────────────────────────────────────────────────
    op.create_table(
        "hifz_goals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("surah_number", sa.Integer, nullable=False),
        sa.Column("mode", _goalmode, nullable=False),
        sa.Column("verses_per_day", sa.Integer, nullable=True),  # QUANTITATIVE: verses to memorize daily
        sa.Column("target_date", sa.Date, nullable=True),        # TEMPORAL: target completion date
        sa.Column("calculated_daily_target", sa.Integer, nullable=False, server_default="1"),
        sa.Column("total_verses", sa.Integer, nullable=False),
        sa.Column("verses_memorized", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_completed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("reciter_id", sa.String(100), nullable=False, server_default="Alafasy_128kbps"),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.UniqueConstraint("student_id", "surah_number", name="uq_hifz_goal_student_surah"),
    )
    op.create_index("ix_hifz_goals_student_id", "hifz_goals", ["student_id"])

    # ── 2. verse_progress ──────────────────────────────────────────────────
    op.create_table(
        "verse_progress",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("goal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("hifz_goals.id"), nullable=True),
        sa.Column("surah_number", sa.Integer, nullable=False),
        sa.Column("verse_number", sa.Integer, nullable=False),
        sa.Column("mastery", _versemastery, nullable=False, server_default="RED"),
        sa.Column("mastery_score", sa.Integer, nullable=False, server_default="0"),  # 0-100
        sa.Column("next_review_date", sa.Date, nullable=False, server_default=sa.func.current_date()),
        sa.Column("review_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("consecutive_successes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_listens", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_practice_seconds", sa.Integer, nullable=False, server_default="0"),
        sa.Column("masking_level", sa.Integer, nullable=False, server_default="0"),  # 0-3, progressively hide words
        sa.Column("last_practiced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.UniqueConstraint("student_id", "surah_number", "verse_number", name="uq_verse_progress"),
    )
    op.create_index("ix_verse_progress_student_id", "verse_progress", ["student_id"])
    op.create_index("ix_verse_review", "verse_progress", ["student_id", "next_review_date"])

    # ── 3. hifz_sessions ───────────────────────────────────────────────────
    op.create_table(
        "hifz_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("goal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("hifz_goals.id"), nullable=True),
        sa.Column("surah_number", sa.Integer, nullable=False),
        sa.Column("loop_count", sa.Integer, nullable=False, server_default="5"),
        sa.Column("pause_seconds", sa.Integer, nullable=False, server_default="5"),
        sa.Column("auto_advance", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("verse_start", sa.Integer, nullable=False),
        sa.Column("verse_end", sa.Integer, nullable=False),
        sa.Column("total_verses_practiced", sa.Integer, nullable=False, server_default="0"),
        sa.Column("verses_marked_known", sa.Integer, nullable=False, server_default="0"),
        sa.Column("duration_seconds", sa.Integer, nullable=True),
        sa.Column("xp_earned", sa.Integer, nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_hifz_sessions_student_id", "hifz_sessions", ["student_id"])

    # ── 4. student_xp ─────────────────────────────────────────────────────
    op.create_table(
        "student_xp",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("total_xp", sa.Integer, nullable=False, server_default="0"),
        sa.Column("level", _studentlevel, nullable=False, server_default="DEBUTANT"),
        sa.Column("xp_from_listening", sa.Integer, nullable=False, server_default="0"),
        sa.Column("xp_from_memorizing", sa.Integer, nullable=False, server_default="0"),
        sa.Column("xp_from_revision", sa.Integer, nullable=False, server_default="0"),
        sa.Column("xp_from_streaks", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_verses_memorized", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_surahs_completed", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_listening_minutes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_sessions", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_student_xp_student_id", "student_xp", ["student_id"])

    # ── 5. student_badges ─────────────────────────────────────────────────
    op.create_table(
        "student_badges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_xp_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("student_xp.id"), nullable=False),
        sa.Column("badge_type", _badgetype, nullable=False),
        sa.Column("badge_detail", sa.String(100), nullable=True),  # e.g., "Juz1", "Surah2", etc.
        sa.Column("earned_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("student_xp_id", "badge_type", "badge_detail", name="uq_student_badge"),
    )
    op.create_index("ix_student_badges_student_xp_id", "student_badges", ["student_xp_id"])


def downgrade() -> None:
    # ── Drop tables in reverse order ─────────────────────────────────────────
    op.drop_table("student_badges")
    op.drop_table("student_xp")
    op.drop_table("hifz_sessions")
    op.drop_table("verse_progress")
    op.drop_table("hifz_goals")

    # ── Drop enum types ─────────────────────────────────────────────────────
    op.execute("DROP TYPE IF EXISTS studentlevel")
    op.execute("DROP TYPE IF EXISTS badgetype")
    op.execute("DROP TYPE IF EXISTS goalmode")
    op.execute("DROP TYPE IF EXISTS versemastery")
