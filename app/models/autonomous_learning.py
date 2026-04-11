"""
Autonomous Learning models — Neuroscience-based Quran vocabulary acquisition.

5 Modules:
  Module 1 — Flash & Recall (50 key words: imprégnation + QCM + verse scan)
  Module 2 — Spatial Particles (20 particles: spatial coding + drag&drop)
  Module 3 — Sense Blocks / Chunking (50 collocations: lego + verse reconstruction)
  Module 4 — Word DNA / Roots (30 roots: tree + intruder + guess meaning)
  Module 5 — Guided Reading (apply all on real surahs)

Spaced Repetition: Leitner Box system (5 boxes)
Audio: EveryAyah API integration
"""
import uuid
import enum
from datetime import datetime, date
from typing import Optional

from sqlalchemy import (
    String, Text, Integer, Float, Boolean, Date, DateTime,
    Enum, ForeignKey, JSON, UniqueConstraint, Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base


# ── Enums ─────────────────────────────────────────────────────────────────────

class WordCategory(str, enum.Enum):
    """Category of a Quran word."""
    PARTICLE    = "PARTICLE"     # حروف — prepositions, conjunctions, etc.
    NOUN        = "NOUN"         # أسماء — nouns, adjectives, pronouns
    VERB        = "VERB"         # أفعال — verbs
    PROPER_NOUN = "PROPER_NOUN"  # أسماء أعلام — names (Allah, Musa, Isa)


class ChunkLevel(str, enum.Enum):
    """Hierarchical level for Quran collocations (Module 3)."""
    PAIR     = "PAIR"      # Level 1: particle + noun (فِي الأَرْضِ)
    TRIPLET  = "TRIPLET"   # Level 2: particle + noun + pronoun (فِي قَلْبِهِ)
    SEGMENT  = "SEGMENT"   # Level 3: real Quranic segment (وَفِي الأَرْضِ آيَاتٌ)


class LeitnerBox(int, enum.Enum):
    """Leitner system — 5 boxes with increasing review intervals."""
    BOX_1 = 1   # New / failed → review daily
    BOX_2 = 2   # Review every 2 days
    BOX_3 = 3   # Review every 4 days
    BOX_4 = 4   # Review every 8 days
    BOX_5 = 5   # Mastered → review every 16 days


class ExerciseType(str, enum.Enum):
    """All exercise types across the 5 modules."""
    # Module 1 — Flash & Recall
    FLASH_RECALL     = "FLASH_RECALL"      # Imprégnation (see word + image + audio)
    QCM_WORD         = "QCM_WORD"          # QCM: recognize word among choices
    VERSE_SCAN       = "VERSE_SCAN"        # Highlight recognized words in a verse

    # Module 2 — Spatial Particles
    SPATIAL_VIEW     = "SPATIAL_VIEW"      # See particle in spatial position
    SPATIAL_DRAG     = "SPATIAL_DRAG"      # Drag & drop particle to correct position
    PARTICLE_FIND    = "PARTICLE_FIND"     # Find particle in a verse

    # Module 3 — Chunking
    CHUNK_IMPRINT    = "CHUNK_IMPRINT"     # See whole chunk (imprégnation)
    CHUNK_LEGO       = "CHUNK_LEGO"        # Reconstruct chunk from pieces
    VERSE_REBUILD    = "VERSE_REBUILD"     # Rebuild verse from chunks

    # Module 4 — Word DNA
    ROOT_DISCOVER    = "ROOT_DISCOVER"     # See root + derivation tree
    ROOT_INTRUDER    = "ROOT_INTRUDER"     # Find the intruder (different root)
    ROOT_GUESS       = "ROOT_GUESS"        # Guess meaning from root knowledge

    # Module 5 — Guided Reading
    GUIDED_SCAN      = "GUIDED_SCAN"       # Full verse scan (all modules combined)
    COMPREHENSION    = "COMPREHENSION"     # Comprehension percentage on a surah


class AutonomousModule(int, enum.Enum):
    """The 5 learning modules."""
    MODULE_1_FLASH_RECALL    = 1
    MODULE_2_PARTICLES       = 2
    MODULE_3_CHUNKING        = 3
    MODULE_4_ROOTS           = 4
    MODULE_5_GUIDED_READING  = 5


class ModulePhase(int, enum.Enum):
    """Each module has 3 phases: See → Do → Apply."""
    PHASE_1_SEE    = 1   # Encodage multimodal
    PHASE_2_DO     = 2   # Récupération active
    PHASE_3_APPLY  = 3   # Transfert en contexte réel


# ── Static content tables ─────────────────────────────────────────────────────

class QuranWord(Base):
    """The 120 most frequent words in the Quran (seed data)."""
    __tablename__ = "quran_words"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    rank: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    arabic: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    transliteration: Mapped[str] = mapped_column(String(200), nullable=False)
    translation_fr: Mapped[str] = mapped_column(String(300), nullable=False)
    translation_en: Mapped[str] = mapped_column(String(300), nullable=True)
    category: Mapped[WordCategory] = mapped_column(Enum(WordCategory), nullable=False)
    frequency: Mapped[int] = mapped_column(Integer, nullable=False)

    # Media (EveryAyah integration)
    audio_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Module assignment
    module: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    # For spatial particles (Module 2): position info
    spatial_position: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # above, below, inside, toward, from, with, between
    # Contrast pair (عَلَى/تَحْتَ taught together)
    contrast_pair_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quran_words.id"), nullable=True
    )

    # Root reference (for Module 4 linkage)
    root_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("arabic_roots.id"), nullable=True
    )

    # Extra data (example verses, context notes)
    extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    root: Mapped["ArabicRoot | None"] = relationship(
        "ArabicRoot", back_populates="words"
    )
    contrast_pair: Mapped["QuranWord | None"] = relationship(
        "QuranWord", remote_side="QuranWord.id"
    )
    leitner_cards: Mapped[list["LeitnerCard"]] = relationship(
        "LeitnerCard", back_populates="word"
    )


class ArabicRoot(Base):
    """30 essential Arabic roots for Module 4 (Word DNA)."""
    __tablename__ = "arabic_roots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    rank: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    root_letters: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False
    )  # e.g., "ك-ت-ب"
    root_bare: Mapped[str] = mapped_column(
        String(10), nullable=False
    )  # e.g., "كتب" (without dashes)
    meaning_fr: Mapped[str] = mapped_column(String(200), nullable=False)
    meaning_en: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Derivations stored as structured JSON for the "tree" visualization
    # [{arabic: "كِتَاب", transliteration: "kitāb", meaning_fr: "livre", meaning_en: "book"}]
    derivations: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Example Quran verse using this root
    example_surah: Mapped[int | None] = mapped_column(Integer, nullable=True)
    example_verse: Mapped[int | None] = mapped_column(Integer, nullable=True)
    example_text_ar: Mapped[str | None] = mapped_column(Text, nullable=True)

    extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    words: Mapped[list["QuranWord"]] = relationship(
        "QuranWord", back_populates="root"
    )


class QuranChunk(Base):
    """50 essential Quran collocations for Module 3 (Chunking)."""
    __tablename__ = "quran_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    rank: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    level: Mapped[ChunkLevel] = mapped_column(Enum(ChunkLevel), nullable=False)

    arabic: Mapped[str] = mapped_column(String(300), nullable=False)
    transliteration: Mapped[str] = mapped_column(String(300), nullable=False)
    translation_fr: Mapped[str] = mapped_column(String(500), nullable=False)
    translation_en: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Component word IDs (references to quran_words)
    word_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)  # [uuid, uuid, ...]

    # Source verse
    surah_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    verse_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    verse_text_ar: Mapped[str | None] = mapped_column(Text, nullable=True)

    audio_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )


# ── Student progress tables ──────────────────────────────────────────────────

class StudentModuleProgress(Base):
    """Tracks a student's progress through the 5 autonomous modules."""
    __tablename__ = "student_module_progress"
    __table_args__ = (
        UniqueConstraint("student_id", "module", name="uq_student_module"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    module: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    current_phase: Mapped[int] = mapped_column(Integer, default=1)  # 1-3

    # Unlocking: module N requires module N-1 completed
    is_unlocked: Mapped[bool] = mapped_column(Boolean, default=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Score metrics
    total_items: Mapped[int] = mapped_column(Integer, default=0)
    items_mastered: Mapped[int] = mapped_column(Integer, default=0)
    accuracy_percent: Mapped[float] = mapped_column(Float, default=0.0)

    # Quran comprehension KPI
    comprehension_percent: Mapped[float] = mapped_column(Float, default=0.0)

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    student: Mapped["User"] = relationship("User", foreign_keys=[student_id])


class LeitnerCard(Base):
    """
    Leitner Box SRS card — one per student per word.

    Box intervals:
      Box 1: review every 1 day (new/failed)
      Box 2: review every 2 days
      Box 3: review every 4 days
      Box 4: review every 8 days
      Box 5: review every 16 days (mastered)

    Correct → move up one box. Wrong → back to Box 1.
    """
    __tablename__ = "leitner_cards"
    __table_args__ = (
        UniqueConstraint("student_id", "word_id", name="uq_leitner_student_word"),
        Index("ix_leitner_review", "student_id", "next_review_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    word_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quran_words.id"), nullable=False
    )

    box: Mapped[int] = mapped_column(Integer, default=1)  # 1-5
    next_review_date: Mapped[date] = mapped_column(Date, default=date.today)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Stats
    total_reviews: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    wrong_count: Mapped[int] = mapped_column(Integer, default=0)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    student: Mapped["User"] = relationship("User", foreign_keys=[student_id])
    word: Mapped["QuranWord"] = relationship("QuranWord", back_populates="leitner_cards")


class ExerciseSession(Base):
    """A learning session — one per student per sitting."""
    __tablename__ = "exercise_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    module: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    phase: Mapped[int] = mapped_column(Integer, nullable=False)   # 1-3

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Session stats
    total_exercises: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    student: Mapped["User"] = relationship("User", foreign_keys=[student_id])
    attempts: Mapped[list["ExerciseAttempt"]] = relationship(
        "ExerciseAttempt", back_populates="session"
    )


class ExerciseAttempt(Base):
    """Individual exercise attempt within a session."""
    __tablename__ = "exercise_attempts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exercise_sessions.id"), nullable=False, index=True
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    exercise_type: Mapped[ExerciseType] = mapped_column(
        Enum(ExerciseType), nullable=False
    )

    # Reference to the item being tested (polymorphic)
    word_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quran_words.id"), nullable=True
    )
    chunk_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quran_chunks.id"), nullable=True
    )
    root_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("arabic_roots.id"), nullable=True
    )
    # For verse scan / guided reading
    surah_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    verse_number: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Result
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # What was shown vs what was answered
    shown_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    answer_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    session: Mapped["ExerciseSession"] = relationship(
        "ExerciseSession", back_populates="attempts"
    )
