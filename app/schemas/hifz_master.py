"""
Pydantic schemas for Hifz Master API.

Maps to models.hifz_master and supports gamified Quranic memorization
with XP progression, badges, and spaced repetition.
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import date, datetime
from uuid import UUID
from typing import Optional
from pydantic import ConfigDict


# ─── Enums (mirrors models) ──────────────────────────────────────────────────

class VerseMasteryEnum(str):
    RED = "RED"
    ORANGE = "ORANGE"
    GREEN = "GREEN"


class GoalModeEnum(str):
    QUANTITATIVE = "QUANTITATIVE"
    TEMPORAL = "TEMPORAL"


class BadgeTypeEnum(str):
    HIZB = "HIZB"
    SURAH_COMPLETE = "SURAH_COMPLETE"
    STREAK_7 = "STREAK_7"
    STREAK_30 = "STREAK_30"
    STREAK_100 = "STREAK_100"
    LEVEL_UP = "LEVEL_UP"
    FIRST_JUZ = "FIRST_JUZ"
    RECITER_10 = "RECITER_10"


class StudentLevelEnum(str):
    DEBUTANT = "DEBUTANT"
    APPRENTI = "APPRENTI"
    HAFIZ_EN_HERBE = "HAFIZ_EN_HERBE"
    HAFIZ_CONFIRME = "HAFIZ_CONFIRME"
    HAFIZ_EXPERT = "HAFIZ_EXPERT"


# ─── Response Schemas (Out) ──────────────────────────────────────────────────


class HifzGoalOut(BaseModel):
    """A memorization goal for a specific surah."""
    id: UUID
    student_id: UUID
    surah_number: int
    mode: str  # GoalMode enum value
    verses_per_day: Optional[int] = None
    target_date: Optional[date] = None
    calculated_daily_target: int
    total_verses: int
    verses_memorized: int
    is_completed: bool
    reciter_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VerseHeatmapEntry(BaseModel):
    """One verse in a heatmap (mastery visualization)."""
    verse_number: int
    mastery: str  # RED, ORANGE, GREEN
    mastery_score: int  # 0-100
    needs_review: bool


class SurahHeatmapOut(BaseModel):
    """Mastery heatmap for all verses in a surah."""
    surah_number: int
    verses: list[VerseHeatmapEntry]


class VerseProgressOut(BaseModel):
    """Detailed progress on a single verse."""
    id: UUID
    student_id: UUID
    goal_id: Optional[UUID] = None
    surah_number: int
    verse_number: int
    mastery: str  # RED, ORANGE, GREEN
    mastery_score: int
    next_review_date: date
    review_count: int
    consecutive_successes: int
    total_listens: int
    total_practice_seconds: int
    masking_level: int
    last_practiced_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HifzSessionOut(BaseModel):
    """A memorization practice session."""
    id: UUID
    student_id: UUID
    goal_id: Optional[UUID] = None
    surah_number: int
    loop_count: int
    pause_seconds: int
    auto_advance: bool
    verse_start: int
    verse_end: int
    total_verses_practiced: int
    verses_marked_known: int
    duration_seconds: Optional[int] = None
    xp_earned: int
    started_at: datetime
    ended_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class BadgeOut(BaseModel):
    """An earned achievement badge."""
    badge_type: str  # BadgeType enum value
    badge_detail: Optional[str] = None
    earned_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentXPOut(BaseModel):
    """Student's XP, level, and badge collection."""
    id: UUID
    student_id: UUID
    total_xp: int
    level: str  # StudentLevel enum value
    xp_from_listening: int
    xp_from_memorizing: int
    xp_from_revision: int
    xp_from_streaks: int
    total_verses_memorized: int
    total_surahs_completed: int
    total_listening_minutes: int
    total_sessions: int
    badges: list[BadgeOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReciterOut(BaseModel):
    """Available Quranic reciter."""
    id: str
    name_ar: str
    name_en: str


# ─── Request Schemas (Create/Update) ─────────────────────────────────────────


class HifzGoalCreate(BaseModel):
    """Request to create a memorization goal."""
    surah_number: int = Field(ge=1, le=114)
    mode: str  # GoalMode enum value: QUANTITATIVE or TEMPORAL
    verses_per_day: Optional[int] = None  # Required if mode == QUANTITATIVE
    target_date: Optional[date] = None    # Required if mode == TEMPORAL
    reciter_id: Optional[str] = "Alafasy_128kbps"


class HifzSessionCreate(BaseModel):
    """Request to start a memorization session."""
    surah_number: int = Field(ge=1, le=114)
    verse_start: int = Field(ge=1, le=286)
    verse_end: int = Field(ge=1, le=286)
    loop_count: int = Field(default=5, ge=1, le=20)
    pause_seconds: int = Field(default=5, ge=0, le=60)
    auto_advance: bool = True


class MarkVerseKnownRequest(BaseModel):
    """Request to mark a verse as known."""
    surah_number: int = Field(ge=1, le=114)
    verse_number: int = Field(ge=1, le=286)


class VerseReviewRequest(BaseModel):
    """Request to review a verse (test student's memorization)."""
    surah_number: int = Field(ge=1, le=114)
    verse_number: int = Field(ge=1, le=286)
    success: bool  # True if student recited correctly
