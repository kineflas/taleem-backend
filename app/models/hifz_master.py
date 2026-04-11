"""
Hifz Master — Gamified Quran memorization module.

Features:
  - Audio loop player with configurable repetition
  - Progressive text masking (blur words as you memorize)
  - Auto-dictée mode (first-letter hints only)
  - Verse-level spaced repetition (Red → Orange → Green)
  - Goal setting (quantitative or temporal)
  - XP system + levels + badges
  - Heatmap revision view
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

class VerseMastery(str, enum.Enum):
    """Mastery status for each verse."""
    RED = "RED"         # New / Difficult → review daily
    ORANGE = "ORANGE"   # Acquiring → review every 2 days
    GREEN = "GREEN"     # Mastered → review every 10 days


class GoalMode(str, enum.Enum):
    """How the student defines their memorization goal."""
    QUANTITATIVE = "QUANTITATIVE"  # "5 verses per day"
    TEMPORAL = "TEMPORAL"          # "Finish surah in 2 weeks"


class BadgeType(str, enum.Enum):
    """Achievement badge types."""
    HIZB = "HIZB"                          # Earned at each 1/60th of Quran
    SURAH_COMPLETE = "SURAH_COMPLETE"      # Completed an entire surah
    STREAK_7 = "STREAK_7"                  # 7-day streak
    STREAK_30 = "STREAK_30"                # 30-day streak
    STREAK_100 = "STREAK_100"              # 100-day streak
    LEVEL_UP = "LEVEL_UP"                  # Level promotion
    FIRST_JUZ = "FIRST_JUZ"                # First juz completed
    RECITER_10 = "RECITER_10"              # 10 verses validated


class StudentLevel(str, enum.Enum):
    """XP-based student levels."""
    DEBUTANT = "DEBUTANT"                          # 0-499 XP
    APPRENTI = "APPRENTI"                          # 500-1999 XP
    HAFIZ_EN_HERBE = "HAFIZ_EN_HERBE"              # 2000-4999 XP
    HAFIZ_CONFIRME = "HAFIZ_CONFIRME"              # 5000-9999 XP
    HAFIZ_EXPERT = "HAFIZ_EXPERT"                  # 10000+ XP


# ── Models ────────────────────────────────────────────────────────

class HifzGoal(Base):
    """Student's memorization goal for a specific surah."""
    __tablename__ = "hifz_goals"
    __table_args__ = (
        UniqueConstraint("student_id", "surah_number", name="uq_hifz_goal_student_surah"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    surah_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Goal configuration
    mode: Mapped[GoalMode] = mapped_column(Enum(GoalMode), nullable=False)
    verses_per_day: Mapped[int | None] = mapped_column(Integer, nullable=True)  # QUANTITATIVE
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)  # TEMPORAL
    calculated_daily_target: Mapped[int] = mapped_column(Integer, default=1)  # auto-computed

    # Progress
    total_verses: Mapped[int] = mapped_column(Integer, nullable=False)
    verses_memorized: Mapped[int] = mapped_column(Integer, default=0)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Reciter preference
    reciter_id: Mapped[str] = mapped_column(String(100), default="Alafasy_128kbps")

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    student: Mapped["User"] = relationship("User", foreign_keys=[student_id])
    verse_progress: Mapped[list["VerseProgress"]] = relationship(
        "VerseProgress", back_populates="goal", cascade="all, delete-orphan"
    )


class VerseProgress(Base):
    """Per-verse mastery tracking with spaced repetition."""
    __tablename__ = "verse_progress"
    __table_args__ = (
        UniqueConstraint("student_id", "surah_number", "verse_number", name="uq_verse_progress"),
        Index("ix_verse_review", "student_id", "next_review_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    goal_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hifz_goals.id"), nullable=True
    )
    surah_number: Mapped[int] = mapped_column(Integer, nullable=False)
    verse_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Mastery (Red → Orange → Green)
    mastery: Mapped[VerseMastery] = mapped_column(
        Enum(VerseMastery), default=VerseMastery.RED
    )
    mastery_score: Mapped[int] = mapped_column(Integer, default=0)  # 0-100

    # Spaced repetition
    next_review_date: Mapped[date] = mapped_column(Date, default=date.today)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    consecutive_successes: Mapped[int] = mapped_column(Integer, default=0)

    # Loop tracking
    total_listens: Mapped[int] = mapped_column(Integer, default=0)
    total_practice_seconds: Mapped[int] = mapped_column(Integer, default=0)

    # Masking progress: what percentage of words are masked (0-100)
    masking_level: Mapped[int] = mapped_column(Integer, default=0)

    last_practiced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    goal: Mapped["HifzGoal | None"] = relationship("HifzGoal", back_populates="verse_progress")


class HifzSession(Base):
    """A memorization/revision session."""
    __tablename__ = "hifz_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    goal_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hifz_goals.id"), nullable=True
    )
    surah_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Session config
    loop_count: Mapped[int] = mapped_column(Integer, default=5)     # Repeat X times
    pause_seconds: Mapped[int] = mapped_column(Integer, default=5)  # Y seconds pause
    auto_advance: Mapped[bool] = mapped_column(Boolean, default=True)

    # Which verses were covered
    verse_start: Mapped[int] = mapped_column(Integer, nullable=False)
    verse_end: Mapped[int] = mapped_column(Integer, nullable=False)

    # Session metrics
    total_verses_practiced: Mapped[int] = mapped_column(Integer, default=0)
    verses_marked_known: Mapped[int] = mapped_column(Integer, default=0)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    student: Mapped["User"] = relationship("User", foreign_keys=[student_id])


class StudentXP(Base):
    """XP and leveling system for gamification."""
    __tablename__ = "student_xp"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )

    total_xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[StudentLevel] = mapped_column(
        Enum(StudentLevel), default=StudentLevel.DEBUTANT
    )

    # XP breakdown
    xp_from_listening: Mapped[int] = mapped_column(Integer, default=0)
    xp_from_memorizing: Mapped[int] = mapped_column(Integer, default=0)
    xp_from_revision: Mapped[int] = mapped_column(Integer, default=0)
    xp_from_streaks: Mapped[int] = mapped_column(Integer, default=0)

    # Cumulative stats
    total_verses_memorized: Mapped[int] = mapped_column(Integer, default=0)
    total_surahs_completed: Mapped[int] = mapped_column(Integer, default=0)
    total_listening_minutes: Mapped[int] = mapped_column(Integer, default=0)
    total_sessions: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    student: Mapped["User"] = relationship("User", foreign_keys=[student_id])
    badges: Mapped[list["StudentBadge"]] = relationship(
        "StudentBadge", back_populates="student_xp"
    )


class StudentBadge(Base):
    """Badges earned by students."""
    __tablename__ = "student_badges"
    __table_args__ = (
        UniqueConstraint("student_xp_id", "badge_type", "badge_detail", name="uq_student_badge"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_xp_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("student_xp.id"), nullable=False
    )
    badge_type: Mapped[BadgeType] = mapped_column(Enum(BadgeType), nullable=False)
    badge_detail: Mapped[str | None] = mapped_column(String(100), nullable=True)  # e.g., "surah_78" or "hizb_60"

    earned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    student_xp: Mapped["StudentXP"] = relationship("StudentXP", back_populates="badges")
