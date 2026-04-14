"""Medine Gamification — flashcards, diagnostic, XP, badges

Revision ID: 006
Revises: 005
Create Date: 2026-04-14

New tables:
- diagnostic_questions: Static question bank for CAT placement test
- diagnostic_sessions: Student test sessions
- diagnostic_results: Final diagnostic scores and recommended paths
- flashcard_cards: Static flashcard content (front/back)
- flashcard_progress: Per-student SRS SM-2 state
- xp_events: XP gain events
- badges: Static badge definitions
- student_badges: Per-student unlocked badges

Altered tables:
- users: Add total_xp, level, diagnostic_completed columns
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. diagnostic_questions ────────────────────────────────────────────
    op.create_table(
        "diagnostic_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("pool", sa.String(1), nullable=False),  # A/B/C
        sa.Column("difficulty", sa.Integer, nullable=False),  # 1/2/3
        sa.Column("skill_tested", sa.String(100), nullable=False),
        sa.Column("lesson_ref", sa.String(20), nullable=True),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("options", sa.JSON, nullable=False),
        sa.Column("correct", sa.Integer, nullable=False),
        sa.Column("explanation", sa.Text, nullable=True),
        sa.Column("adaptive_hint", sa.Text, nullable=True),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
    )

    # ── 2. diagnostic_sessions ─────────────────────────────────────────────
    op.create_table(
        "diagnostic_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_completed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("answers", sa.JSON, nullable=True),
        sa.Column("current_pool", sa.String(1), nullable=False, server_default="'A'"),
        sa.Column("current_pool_index", sa.Integer, nullable=False, server_default="0"),
    )

    # ── 3. diagnostic_results ──────────────────────────────────────────────
    op.create_table(
        "diagnostic_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("diagnostic_sessions.id"), nullable=False, unique=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("score", sa.Integer, nullable=False),
        sa.Column("level", sa.String(50), nullable=False),
        sa.Column("level_message", sa.Text, nullable=True),
        sa.Column("skill_scores", sa.JSON, nullable=True),
        sa.Column("recommended_path", sa.JSON, nullable=True),
        sa.Column("estimated_duration", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ── 4. flashcard_cards ─────────────────────────────────────────────────
    op.create_table(
        "flashcard_cards",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("lesson_number", sa.Integer, nullable=False),
        sa.Column("part_number", sa.Integer, nullable=False),
        sa.Column("card_id_str", sa.String(20), nullable=False, unique=True),
        sa.Column("front_ar", sa.Text, nullable=False),
        sa.Column("back_fr", sa.Text, nullable=False),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("arabic_example", sa.Text, nullable=True),
        sa.Column("french_example", sa.Text, nullable=True),
        sa.Column("audio_key", sa.String(200), nullable=True),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ── 5. flashcard_progress ──────────────────────────────────────────────
    op.create_table(
        "flashcard_progress",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("card_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("flashcard_cards.id"), nullable=False),
        sa.Column("ease_factor", sa.Float, nullable=False, server_default="2.5"),
        sa.Column("interval_days", sa.Integer, nullable=False, server_default="0"),
        sa.Column("repetitions", sa.Integer, nullable=False, server_default="0"),
        sa.Column("next_review", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("last_quality", sa.Integer, nullable=True),
        sa.Column("review_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("student_id", "card_id", name="uq_flashcard_student_card"),
    )

    # ── 6. xp_events ───────────────────────────────────────────────────────
    op.create_table(
        "xp_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("source_id", sa.String(100), nullable=True),
        sa.Column("xp_earned", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ── 7. badges ──────────────────────────────────────────────────────────
    op.create_table(
        "badges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("name_fr", sa.String(200), nullable=False),
        sa.Column("description_fr", sa.Text, nullable=True),
        sa.Column("icon", sa.String(100), nullable=True),
        sa.Column("condition_type", sa.String(50), nullable=False),
        sa.Column("condition_value", sa.JSON, nullable=True),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
    )

    # ── 8. medine_badge_unlocks ───────────────────────────────────────────
    op.create_table(
        "medine_badge_unlocks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("badge_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("badges.id"), nullable=False),
        sa.Column("unlocked_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("student_id", "badge_id", name="uq_medine_badge_unlock"),
    )

    # ── Alter users table ──────────────────────────────────────────────────
    op.add_column("users", sa.Column("total_xp", sa.Integer, nullable=False, server_default="0"))
    op.add_column("users", sa.Column("level", sa.Integer, nullable=False, server_default="1"))
    op.add_column("users", sa.Column("diagnostic_completed", sa.Boolean, nullable=False, server_default="false"))


def downgrade() -> None:
    # ── Drop added columns from users table ──────────────────────────────────
    op.drop_column("users", "diagnostic_completed")
    op.drop_column("users", "level")
    op.drop_column("users", "total_xp")

    # ── Drop tables in reverse order ─────────────────────────────────────────
    op.drop_table("medine_badge_unlocks")
    op.drop_table("badges")
    op.drop_table("xp_events")
    op.drop_table("flashcard_progress")
    op.drop_table("flashcard_cards")
    op.drop_table("diagnostic_results")
    op.drop_table("diagnostic_sessions")
    op.drop_table("diagnostic_questions")
