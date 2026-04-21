"""
Pydantic schemas for Hifz Master V2 API.

Covers: Wird sessions, exercises, SRS 7-tier, enriched surah content, journey map.
"""
from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from uuid import UUID
from typing import Optional


# ─── Enums (as string constants for JSON) ────────────────────────

class WirdStatusEnum:
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"


class ExerciseTypeEnum:
    PUZZLE = "PUZZLE"
    MOT_MANQUANT = "MOT_MANQUANT"
    VERSET_SUIVANT = "VERSET_SUIVANT"
    ECOUTE = "ECOUTE"
    DICTEE = "DICTEE"
    VRAI_FAUX = "VRAI_FAUX"
    DEBUT_FIN = "DEBUT_FIN"
    VERSET_MIROIR = "VERSET_MIROIR"


class SrsTierEnum:
    NOUVEAU = 1
    FRAGILE = 2
    EN_COURS = 3
    ACQUIS = 4
    SOLIDE = 5
    MAITRISE = 6
    ANCRE = 7


# ─── Enriched Surah Content ─────────────────────────────────────

class KeyWordOut(BaseModel):
    ar: str
    fr: str
    root: str = ""


class EnrichedVerseOut(BaseModel):
    """A single verse with all pedagogical metadata."""
    number: int
    text_ar: str
    text_fr: str = ""
    context_fr: str = ""
    words: list[str]
    audio_timing: list[float] = []
    key_word: Optional[KeyWordOut] = None


class VerseConnectionOut(BaseModel):
    from_verse: int
    to_verse: int
    hint_fr: str


class EnrichedSurahOut(BaseModel):
    """Full enriched surah data for the Wird flow."""
    surah_number: int
    name_ar: str
    name_fr: str
    name_transliteration: str = ""
    revelation: str = ""
    verse_count: int
    theme_fr: str = ""
    intro_fr: str = ""
    verses: list[EnrichedVerseOut]
    connections: list[VerseConnectionOut] = []


# ─── Wird Session ────────────────────────────────────────────────

class WirdVerseInfo(BaseModel):
    """Info about a single verse in a Wird bloc."""
    surah_number: int
    verse_number: int
    text_ar: str = ""
    mastery_score: int = 0
    srs_tier: int = 1
    stars: int = 0


class WirdBlocOut(BaseModel):
    """A bloc within the Wird (JADID, QARIB, or BAID)."""
    bloc_type: str  # JADID, QARIB, BAID
    label_ar: str   # جديد, قريب, بعيد
    verses: list[WirdVerseInfo]


class WirdTodayOut(BaseModel):
    """The Wird composition for today."""
    wird_session_id: Optional[UUID] = None  # None if not started yet
    date: date
    blocs: list[WirdBlocOut]
    estimated_duration_minutes: int
    total_verses: int
    # Reciter for audio
    reciter_folder: str = "Alafasy_128kbps"
    # If already started, progress info
    status: str = "NOT_STARTED"  # NOT_STARTED, IN_PROGRESS, COMPLETED
    progress_percent: int = 0


class WirdStartRequest(BaseModel):
    """Request to start (or resume) today's Wird."""
    surah_number: Optional[int] = Field(default=None, ge=1, le=114)


class SuggestedSurahOut(BaseModel):
    """A suggested surah for the student to study."""
    surah_number: int
    name_ar: str
    name_fr: str
    total_verses: int
    verses_started: int = 0
    verses_remaining: int = 0
    next_verse: int = 1
    average_score: float = 0.0
    has_review_due: bool = False
    review_count: int = 0
    reason: str = ""  # "in_progress", "suggested", "review_due"


class SuggestedSurahsOut(BaseModel):
    """Response for suggested surahs endpoint."""
    current_surah: Optional[SuggestedSurahOut] = None
    suggestions: list[SuggestedSurahOut] = []
    review_due_surahs: list[SuggestedSurahOut] = []


class WirdSessionOut(BaseModel):
    """A completed or in-progress Wird session."""
    id: UUID
    student_id: UUID
    date: date
    status: str
    new_verses_count: int
    qarib_count: int
    baid_count: int
    total_exercises: int
    correct_exercises: int
    duration_seconds: Optional[int] = None
    xp_earned: int
    started_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class WirdCompleteRequest(BaseModel):
    """Request body to complete a Wird session."""
    duration_seconds: int = Field(ge=0)
    total_exercises: int = Field(ge=0)
    correct_exercises: int = Field(ge=0)


# ─── Exercise Answer ─────────────────────────────────────────────

class ExerciseAnswerRequest(BaseModel):
    """Submit an exercise answer."""
    wird_session_id: Optional[UUID] = None
    surah_number: int = Field(ge=1, le=114)
    verse_number: int = Field(ge=1, le=286)
    exercise_type: str  # ExerciseType enum value
    is_correct: bool
    response_time_ms: Optional[int] = None
    attempt_number: int = Field(default=1, ge=1)
    metadata: Optional[dict] = None  # Exercise-specific data


class ExerciseAnswerOut(BaseModel):
    """Response after submitting an exercise answer."""
    id: UUID
    mastery_score_before: int
    mastery_score_after: int
    srs_tier_before: int
    srs_tier_after: int
    xp_earned: int
    next_review_date: date
    stars: int  # 0-3


# ─── Verse Progress V2 (extends V1) ─────────────────────────────

class VerseProgressV2Out(BaseModel):
    """Verse progress with V2 SRS tier info."""
    surah_number: int
    verse_number: int
    mastery_score: int  # 0-100
    srs_tier: int  # 1-7
    srs_tier_label: str  # "Nouveau", "Fragile", etc.
    srs_tier_color: str  # hex color
    stars: int  # 0-3
    next_review_date: date
    review_count: int
    total_exercises_played: int = 0
    last_practiced_at: Optional[datetime] = None


# ─── Journey Map ─────────────────────────────────────────────────

class SurahMapEntry(BaseModel):
    """A surah entry in the journey map."""
    surah_number: int
    name_ar: str
    name_fr: str
    total_verses: int
    verses_started: int = 0
    verses_mastered: int = 0  # score >= 70
    total_stars: int = 0
    max_stars: int = 0  # total_verses * 3
    average_score: float = 0.0
    is_completed: bool = False
    has_goal: bool = False


class JourneyMapOut(BaseModel):
    """The full journey map for the student."""
    surahs: list[SurahMapEntry]
    total_verses_memorized: int = 0
    total_stars: int = 0
    current_streak: int = 0
    # Student profile
    total_xp: int = 0
    level: str = "DEBUTANT"
    title_ar: str = "طالب"
    title_fr: str = "Talib"


# ─── Step Results (for frontend sync) ───────────────────────────

class StepResultRequest(BaseModel):
    """Submit result of a step within the Wird verse flow."""
    wird_session_id: Optional[UUID] = None
    surah_number: int = Field(ge=1, le=114)
    verse_number: int = Field(ge=1, le=286)
    step: str  # NOUR, TIKRAR, TAMRIN, TASMI, NATIJA
    score: int = Field(ge=0, le=100)
    duration_seconds: int = Field(ge=0)
    metadata: Optional[dict] = None  # Step-specific data (e.g., exercises detail)


class StepResultOut(BaseModel):
    """Response after submitting a step result."""
    mastery_score: int
    srs_tier: int
    stars: int
    xp_earned: int
    next_review_date: date


# ─── Checkpoint (Phase 2) ─────────────────────────────────────

class CheckpointVerseScore(BaseModel):
    """Score for a single verse within a checkpoint."""
    surah_number: int = Field(ge=1, le=114)
    verse_number: int = Field(ge=1, le=286)
    score: int = Field(ge=0, le=100)


class CheckpointCompleteRequest(BaseModel):
    """Request to complete a checkpoint with multi-verse scores."""
    wird_session_id: Optional[UUID] = None
    surah_number: int = Field(ge=1, le=114)
    verse_start: int = Field(ge=1, le=286)
    verse_end: int = Field(ge=1, le=286)
    # Scores by checkpoint step
    tartib_score: int = Field(ge=0, le=100)
    takamul_score: int = Field(ge=0, le=100)
    tasmi_score: int = Field(ge=0, le=100)
    rabita_score: Optional[int] = Field(default=None, ge=0, le=100)  # Phase 3
    # Per-verse scores (optional, for granular SRS update)
    verse_scores: list[CheckpointVerseScore] = []
    duration_seconds: int = Field(ge=0)


class CheckpointCompleteOut(BaseModel):
    """Response after completing a checkpoint."""
    global_score: int
    stars: int
    xp_earned: int
    verses_updated: int
    scores_by_step: dict  # {"tartib": 80, "takamul": 90, "rabita": 75, "tasmi": 85}


# ─── Quick Verify (Phase 3 — Mode Rapide) ────────────────────────

class QuickVerifyVerseScore(BaseModel):
    """Score for a single verse in quick verify."""
    verse_number: int = Field(ge=1, le=286)
    score: int = Field(ge=0, le=100)


class QuickVerifyRequest(BaseModel):
    """Request for quick surah verification (Mode Rapide)."""
    tartib_score: int = Field(ge=0, le=100)
    takamul_score: int = Field(ge=0, le=100)
    tasmi_score: int = Field(ge=0, le=100)
    verse_scores: list[QuickVerifyVerseScore] = []
    duration_seconds: int = Field(ge=0)


class QuickVerifyOut(BaseModel):
    """Response after quick verification."""
    global_score: int
    stars: int
    xp_earned: int
    verses_updated: int
    tier_ups: int
    scores_by_step: dict


# ── Audio Revision Playlist ──────────────────────────────────────

class RevisionVerseOut(BaseModel):
    """A single verse entry in the audio revision playlist."""
    surah_number: int
    verse_number: int
    surah_name_ar: str
    tier: str
    mastery_score: int
    next_review_date: str  # ISO date


class AudioRevisionPlaylistOut(BaseModel):
    """Playlist of verses for audio revision, ordered by urgency."""
    verses: list[RevisionVerseOut]
    total_listens: int  # Sum of adaptive repeats
    estimated_minutes: int
