"""Autonomous Learning — 7 tables for neuroscience-based Quran vocabulary acquisition

Revision ID: 004
Revises: 003
Create Date: 2026-04-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Pre-define enum types with create_type=False — we manage creation ourselves
_wordcategory = postgresql.ENUM(
    "PARTICLE", "NOUN", "VERB", "PROPER_NOUN",
    name="wordcategory", create_type=False
)
_chunklevel = postgresql.ENUM(
    "PAIR", "TRIPLET", "SEGMENT",
    name="chunklevel", create_type=False
)
_exercisetype = postgresql.ENUM(
    "FLASH_RECALL", "QCM_WORD", "VERSE_SCAN",
    "SPATIAL_VIEW", "SPATIAL_DRAG", "PARTICLE_FIND",
    "CHUNK_IMPRINT", "CHUNK_LEGO", "VERSE_REBUILD",
    "ROOT_DISCOVER", "ROOT_INTRUDER", "ROOT_GUESS",
    "GUIDED_SCAN", "COMPREHENSION",
    name="exercisetype", create_type=False
)

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Create enum types ───────────────────────────────────────────────────
    op.execute("CREATE TYPE wordcategory AS ENUM ('PARTICLE', 'NOUN', 'VERB', 'PROPER_NOUN')")
    op.execute("CREATE TYPE chunklevel AS ENUM ('PAIR', 'TRIPLET', 'SEGMENT')")
    op.execute("CREATE TYPE exercisetype AS ENUM ('FLASH_RECALL', 'QCM_WORD', 'VERSE_SCAN', 'SPATIAL_VIEW', 'SPATIAL_DRAG', 'PARTICLE_FIND', 'CHUNK_IMPRINT', 'CHUNK_LEGO', 'VERSE_REBUILD', 'ROOT_DISCOVER', 'ROOT_INTRUDER', 'ROOT_GUESS', 'GUIDED_SCAN', 'COMPREHENSION')")

    # ── 1. arabic_roots (created first, needed by quran_words FK) ──────────
    op.create_table(
        "arabic_roots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("rank", sa.Integer, unique=True, nullable=False),
        sa.Column("root_letters", sa.String(20), unique=True, nullable=False),
        sa.Column("root_bare", sa.String(10), nullable=False),
        sa.Column("meaning_fr", sa.String(200), nullable=False),
        sa.Column("meaning_en", sa.String(200), nullable=True),
        sa.Column("derivations", postgresql.JSON, nullable=True),
        sa.Column("example_surah", sa.Integer, nullable=True),
        sa.Column("example_verse", sa.Integer, nullable=True),
        sa.Column("example_text_ar", sa.Text, nullable=True),
        sa.Column("extra_data", postgresql.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_arabic_roots_rank", "arabic_roots", ["rank"])

    # ── 2. quran_words ──────────────────────────────────────────────────────
    op.create_table(
        "quran_words",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("rank", sa.Integer, unique=True, nullable=False),
        sa.Column("arabic", sa.String(100), nullable=False, index=True),
        sa.Column("transliteration", sa.String(200), nullable=False),
        sa.Column("translation_fr", sa.String(300), nullable=False),
        sa.Column("translation_en", sa.String(300), nullable=True),
        sa.Column("category", _wordcategory, nullable=False),
        sa.Column("frequency", sa.Integer, nullable=False),
        sa.Column("audio_url", sa.String(500), nullable=True),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("module", sa.Integer, nullable=False, server_default="1"),
        sa.Column("spatial_position", sa.String(20), nullable=True),
        sa.Column("contrast_pair_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("quran_words.id"), nullable=True),
        sa.Column("root_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("arabic_roots.id"), nullable=True),
        sa.Column("extra_data", postgresql.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_quran_words_rank", "quran_words", ["rank"])
    op.create_index("ix_quran_words_root_id", "quran_words", ["root_id"])

    # ── 3. quran_chunks ─────────────────────────────────────────────────────
    op.create_table(
        "quran_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("rank", sa.Integer, unique=True, nullable=False),
        sa.Column("level", _chunklevel, nullable=False),
        sa.Column("arabic", sa.String(300), nullable=False),
        sa.Column("transliteration", sa.String(300), nullable=False),
        sa.Column("translation_fr", sa.String(500), nullable=False),
        sa.Column("translation_en", sa.String(500), nullable=True),
        sa.Column("word_ids", postgresql.JSON, nullable=True),
        sa.Column("surah_number", sa.Integer, nullable=True),
        sa.Column("verse_number", sa.Integer, nullable=True),
        sa.Column("verse_text_ar", sa.Text, nullable=True),
        sa.Column("audio_url", sa.String(500), nullable=True),
        sa.Column("extra_data", postgresql.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_quran_chunks_rank", "quran_chunks", ["rank"])

    # ── 4. student_module_progress ──────────────────────────────────────────
    op.create_table(
        "student_module_progress",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("module", sa.Integer, nullable=False),
        sa.Column("current_phase", sa.Integer, nullable=False, server_default="1"),
        sa.Column("is_unlocked", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_completed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("total_items", sa.Integer, nullable=False, server_default="0"),
        sa.Column("items_mastered", sa.Integer, nullable=False, server_default="0"),
        sa.Column("accuracy_percent", sa.Float, nullable=False, server_default="0"),
        sa.Column("comprehension_percent", sa.Float, nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.UniqueConstraint("student_id", "module", name="uq_student_module"),
    )
    op.create_index("ix_student_module_progress_student_id", "student_module_progress", ["student_id"])

    # ── 5. leitner_cards ────────────────────────────────────────────────────
    op.create_table(
        "leitner_cards",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("word_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("quran_words.id"), nullable=False),
        sa.Column("box", sa.Integer, nullable=False, server_default="1"),
        sa.Column("next_review_date", sa.Date, nullable=False, server_default=sa.func.current_date()),
        sa.Column("last_reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_reviews", sa.Integer, nullable=False, server_default="0"),
        sa.Column("correct_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("wrong_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("current_streak", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.UniqueConstraint("student_id", "word_id", name="uq_leitner_student_word"),
    )
    op.create_index("ix_leitner_cards_student_id", "leitner_cards", ["student_id"])
    op.create_index("ix_leitner_review", "leitner_cards", ["student_id", "next_review_date"])

    # ── 6. exercise_sessions ────────────────────────────────────────────────
    op.create_table(
        "exercise_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("module", sa.Integer, nullable=False),
        sa.Column("phase", sa.Integer, nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_exercises", sa.Integer, nullable=False, server_default="0"),
        sa.Column("correct_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("duration_seconds", sa.Integer, nullable=True),
    )
    op.create_index("ix_exercise_sessions_student_id", "exercise_sessions", ["student_id"])

    # ── 7. exercise_attempts ────────────────────────────────────────────────
    op.create_table(
        "exercise_attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("exercise_sessions.id"), nullable=False, index=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("exercise_type", _exercisetype, nullable=False),
        sa.Column("word_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("quran_words.id"), nullable=True),
        sa.Column("chunk_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("quran_chunks.id"), nullable=True),
        sa.Column("root_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("arabic_roots.id"), nullable=True),
        sa.Column("surah_number", sa.Integer, nullable=True),
        sa.Column("verse_number", sa.Integer, nullable=True),
        sa.Column("is_correct", sa.Boolean, nullable=False),
        sa.Column("response_time_ms", sa.Integer, nullable=True),
        sa.Column("shown_data", postgresql.JSON, nullable=True),
        sa.Column("answer_data", postgresql.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_exercise_attempts_session_id", "exercise_attempts", ["session_id"])
    op.create_index("ix_exercise_attempts_student_id", "exercise_attempts", ["student_id"])


def downgrade() -> None:
    # ── Drop tables in reverse order ─────────────────────────────────────────
    op.drop_table("exercise_attempts")
    op.drop_table("exercise_sessions")
    op.drop_table("leitner_cards")
    op.drop_table("student_module_progress")
    op.drop_table("quran_chunks")
    op.drop_table("quran_words")
    op.drop_table("arabic_roots")

    # ── Drop enum types ─────────────────────────────────────────────────────
    op.execute("DROP TYPE IF EXISTS exercisetype")
    op.execute("DROP TYPE IF EXISTS chunklevel")
    op.execute("DROP TYPE IF EXISTS wordcategory")
