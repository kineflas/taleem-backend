"""Hifz Master V2 — Wird sessions, verse exercises, SRS 7-tier support

Revision ID: 009
Revises: 008
Create Date: 2026-04-19

New tables:
- wird_sessions: Daily Wird sessions (JADID + QARIB + BA'ID)
- verse_exercises: Per-exercise log for each verse

New columns on verse_progress:
- srs_tier: Integer (1-7) for 7-tier SRS

New enums:
- wirdstatus: IN_PROGRESS, COMPLETED, SKIPPED
- exercisetype: PUZZLE, MOT_MANQUANT, VERSET_SUIVANT, ECOUTE, DICTEE, VRAI_FAUX, DEBUT_FIN, VERSET_MIROIR
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Pre-define enum types
_wirdstatus = postgresql.ENUM(
    "IN_PROGRESS", "COMPLETED", "SKIPPED",
    name="wirdstatus", create_type=False
)

_exercisetype = postgresql.ENUM(
    "PUZZLE", "MOT_MANQUANT", "VERSET_SUIVANT", "ECOUTE",
    "DICTEE", "VRAI_FAUX", "DEBUT_FIN", "VERSET_MIROIR",
    name="exercisetype", create_type=False
)


# revision identifiers
revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Create enums ─────────────────────────────────────────────
    op.execute("CREATE TYPE wirdstatus AS ENUM ('IN_PROGRESS', 'COMPLETED', 'SKIPPED')")
    op.execute(
        "CREATE TYPE exercisetype AS ENUM ("
        "'PUZZLE', 'MOT_MANQUANT', 'VERSET_SUIVANT', 'ECOUTE', "
        "'DICTEE', 'VRAI_FAUX', 'DEBUT_FIN', 'VERSET_MIROIR')"
    )

    # ── wird_sessions ────────────────────────────────────────────
    op.create_table(
        "wird_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("student_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("date", sa.Date, nullable=False, server_default=sa.text("CURRENT_DATE")),
        sa.Column("status", _wirdstatus, nullable=False,
                  server_default=sa.text("'IN_PROGRESS'")),
        sa.Column("new_verses_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("qarib_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("baid_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_exercises", sa.Integer, nullable=False, server_default="0"),
        sa.Column("correct_exercises", sa.Integer, nullable=False, server_default="0"),
        sa.Column("duration_seconds", sa.Integer, nullable=True),
        sa.Column("xp_earned", sa.Integer, nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index(
        "ix_wird_student_date",
        "wird_sessions",
        ["student_id", "date"],
    )

    # ── verse_exercises ──────────────────────────────────────────
    op.create_table(
        "verse_exercises",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("student_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("wird_session_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("wird_sessions.id"), nullable=True),
        sa.Column("surah_number", sa.Integer, nullable=False),
        sa.Column("verse_number", sa.Integer, nullable=False),
        sa.Column("exercise_type", _exercisetype, nullable=False),
        sa.Column("is_correct", sa.Boolean, nullable=False),
        sa.Column("response_time_ms", sa.Integer, nullable=True),
        sa.Column("attempt_number", sa.Integer, nullable=False, server_default="1"),
        sa.Column("metadata_json", postgresql.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text("NOW()")),
    )

    op.create_index(
        "ix_exercise_student_verse",
        "verse_exercises",
        ["student_id", "surah_number", "verse_number"],
    )

    # ── Add srs_tier to verse_progress ───────────────────────────
    op.add_column(
        "verse_progress",
        sa.Column("srs_tier", sa.Integer, nullable=True, server_default="1"),
    )

    # Backfill srs_tier from mastery_score
    op.execute("""
        UPDATE verse_progress SET srs_tier = CASE
            WHEN mastery_score >= 95 THEN 7
            WHEN mastery_score >= 85 THEN 6
            WHEN mastery_score >= 70 THEN 5
            WHEN mastery_score >= 55 THEN 4
            WHEN mastery_score >= 40 THEN 3
            WHEN mastery_score >= 20 THEN 2
            ELSE 1
        END
    """)


def downgrade() -> None:
    op.drop_column("verse_progress", "srs_tier")
    op.drop_table("verse_exercises")
    op.drop_table("wird_sessions")
    op.execute("DROP TYPE IF EXISTS exercisetype")
    op.execute("DROP TYPE IF EXISTS wirdstatus")
