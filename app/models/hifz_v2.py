"""
Hifz Master V2 — Wird-based Quran memorization with 7-tier SRS.

New tables:
  - wird_sessions: Daily Wird session (JADID + QARIB + BA'ID blocs)
  - verse_exercises: Individual exercise logs per verse

Extends verse_progress with srs_tier (7 levels) while keeping
backward-compatible mastery (RED/ORANGE/GREEN).
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


# ── Enums ─────────────────────────────────────────────────────────

class WirdStatus(str, enum.Enum):
    """Status of a daily Wird session."""
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"


class ExerciseType(str, enum.Enum):
    """Types of interactive exercises."""
    PUZZLE = "PUZZLE"                   # ترتيب — Reorder words
    MOT_MANQUANT = "MOT_MANQUANT"       # إكمال — Fill the blank (QCM)
    VERSET_SUIVANT = "VERSET_SUIVANT"   # وصل  — What comes next?
    ECOUTE = "ECOUTE"                   # سمع  — Listen & identify
    DICTEE = "DICTEE"                   # إملاء — Dictation
    VRAI_FAUX = "VRAI_FAUX"             # صح/خطأ — True or False
    DEBUT_FIN = "DEBUT_FIN"             # بداية/نهاية — Beginning/End
    VERSET_MIROIR = "VERSET_MIROIR"     # مرآة — ASR recitation check


class SrsTier(int, enum.Enum):
    """7-tier SRS system for verse memorization."""
    NOUVEAU = 1     # J+1,  score 0-19%
    FRAGILE = 2     # J+2,  score 20-39%
    EN_COURS = 3    # J+4,  score 40-54%
    ACQUIS = 4      # J+7,  score 55-69%
    SOLIDE = 5      # J+14, score 70-84%
    MAITRISE = 6    # J+30, score 85-94%
    ANCRE = 7       # J+90, score 95-100%


class WirdBloc(str, enum.Enum):
    """The three blocs composing a Wird session."""
    JADID = "JADID"   # New verses (full 5-step flow)
    QARIB = "QARIB"   # Recent review (J+1 to J+7)
    BAID = "BAID"     # Distant review (J+7+)


# ── SRS Configuration ────────────────────────────────────────────

SRS_TIERS = {
    SrsTier.NOUVEAU:  {"interval_days": 1,  "min_score": 0,  "max_score": 19,  "label_fr": "Nouveau",   "color": "#B91C1C"},
    SrsTier.FRAGILE:  {"interval_days": 2,  "min_score": 20, "max_score": 39,  "label_fr": "Fragile",   "color": "#DC2626"},
    SrsTier.EN_COURS: {"interval_days": 4,  "min_score": 40, "max_score": 54,  "label_fr": "En cours",  "color": "#F97316"},
    SrsTier.ACQUIS:   {"interval_days": 7,  "min_score": 55, "max_score": 69,  "label_fr": "Acquis",    "color": "#EAB308"},
    SrsTier.SOLIDE:   {"interval_days": 14, "min_score": 70, "max_score": 84,  "label_fr": "Solide",    "color": "#84CC16"},
    SrsTier.MAITRISE: {"interval_days": 30, "min_score": 85, "max_score": 94,  "label_fr": "Maîtrisé",  "color": "#22C55E"},
    SrsTier.ANCRE:    {"interval_days": 90, "min_score": 95, "max_score": 100, "label_fr": "Ancré",     "color": "#BFA04A"},
}


def tier_from_score(score: int) -> SrsTier:
    """Determine SRS tier from mastery score (0-100)."""
    if score >= 95:
        return SrsTier.ANCRE
    elif score >= 85:
        return SrsTier.MAITRISE
    elif score >= 70:
        return SrsTier.SOLIDE
    elif score >= 55:
        return SrsTier.ACQUIS
    elif score >= 40:
        return SrsTier.EN_COURS
    elif score >= 20:
        return SrsTier.FRAGILE
    else:
        return SrsTier.NOUVEAU


# ── Models ────────────────────────────────────────────────────────

class WirdSession(Base):
    """A daily Wird session containing JADID + QARIB + BA'ID blocs."""
    __tablename__ = "wird_sessions"
    __table_args__ = (
        Index("ix_wird_student_date", "student_id", "date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    status: Mapped[WirdStatus] = mapped_column(
        Enum(WirdStatus), default=WirdStatus.IN_PROGRESS
    )

    # Bloc counts (how many verses in each bloc)
    new_verses_count: Mapped[int] = mapped_column(Integer, default=0)
    qarib_count: Mapped[int] = mapped_column(Integer, default=0)
    baid_count: Mapped[int] = mapped_column(Integer, default=0)

    # Exercise stats
    total_exercises: Mapped[int] = mapped_column(Integer, default=0)
    correct_exercises: Mapped[int] = mapped_column(Integer, default=0)

    # Session metrics
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    student: Mapped["User"] = relationship("User", foreign_keys=[student_id])
    exercises: Mapped[list["VerseExercise"]] = relationship(
        "VerseExercise", back_populates="wird_session", cascade="all, delete-orphan"
    )


class VerseExercise(Base):
    """Log of an individual exercise played for a verse."""
    __tablename__ = "verse_exercises"
    __table_args__ = (
        Index("ix_exercise_student_verse", "student_id", "surah_number", "verse_number"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    wird_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wird_sessions.id"), nullable=True
    )

    surah_number: Mapped[int] = mapped_column(Integer, nullable=False)
    verse_number: Mapped[int] = mapped_column(Integer, nullable=False)

    exercise_type: Mapped[ExerciseType] = mapped_column(Enum(ExerciseType), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    attempt_number: Mapped[int] = mapped_column(Integer, default=1)

    # Optional: exercise-specific data (e.g., which words were wrong)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    wird_session: Mapped["WirdSession | None"] = relationship(
        "WirdSession", back_populates="exercises"
    )
