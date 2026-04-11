"""
Pydantic schemas for Autonomous Learning API.

Maps to models.autonomous_learning and supports the 5-module neuroscience-based
Quran vocabulary acquisition system with Leitner spaced repetition.
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import date, datetime
from uuid import UUID
from typing import Optional
from pydantic import ConfigDict

from ..models.autonomous_learning import (
    WordCategory,
    ChunkLevel,
    ExerciseType,
    AutonomousModule,
    ModulePhase,
)


# ─── Response Schemas (Out) ──────────────────────────────────────────────────


class QuranWordOut(BaseModel):
    """A Quran word from the core vocabulary (Module 1-4)."""
    id: UUID
    rank: int
    arabic: str
    transliteration: str
    translation_fr: str
    translation_en: str | None = None
    category: WordCategory
    frequency: int
    audio_url: str | None = None
    image_url: str | None = None
    module: int
    spatial_position: str | None = None  # above, below, inside, toward, from, with, between
    extra_data: dict | None = None

    model_config = ConfigDict(from_attributes=True)


class ArabicRootOut(BaseModel):
    """An Arabic root with derivations (Module 4)."""
    id: UUID
    rank: int
    root_letters: str  # e.g., "ك-ت-ب"
    root_bare: str    # e.g., "كتب"
    meaning_fr: str
    meaning_en: str | None = None
    derivations: list | None = None  # [{arabic: ..., transliteration: ..., meaning_fr: ..., meaning_en: ...}]
    example_surah: int | None = None
    example_verse: int | None = None
    example_text_ar: str | None = None

    model_config = ConfigDict(from_attributes=True)


class QuranChunkOut(BaseModel):
    """A Quran collocation/chunk (Module 3)."""
    id: UUID
    rank: int
    level: ChunkLevel
    arabic: str
    transliteration: str
    translation_fr: str
    translation_en: str | None = None
    word_ids: list | None = None  # [UUID, UUID, ...]
    surah_number: int | None = None
    verse_number: int | None = None
    verse_text_ar: str | None = None
    audio_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class LeitnerCardOut(BaseModel):
    """A spaced repetition card (Leitner Box system)."""
    id: UUID
    word_id: UUID
    box: int  # 1-5
    next_review_date: date
    last_reviewed_at: datetime | None = None
    total_reviews: int
    correct_count: int
    wrong_count: int
    current_streak: int
    word: QuranWordOut  # Nested word object

    model_config = ConfigDict(from_attributes=True)


class SRSStatsOut(BaseModel):
    """Overall spaced repetition statistics for a student."""
    box_1_count: int
    box_2_count: int
    box_3_count: int
    box_4_count: int
    box_5_count: int
    total_cards: int
    mastered_count: int  # Cards in box 5
    due_today_count: int  # Cards due for review today
    accuracy_percent: float  # (correct_count / total_reviews) * 100


class ModuleProgressOut(BaseModel):
    """A student's progress through one of the 5 modules."""
    id: UUID
    module: int  # 1-5
    current_phase: int  # 1-3
    is_unlocked: bool
    is_completed: bool
    total_items: int
    items_mastered: int
    accuracy_percent: float
    comprehension_percent: float
    started_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ExerciseSessionOut(BaseModel):
    """A learning session (one sitting of exercises)."""
    id: UUID
    module: int  # 1-5
    phase: int  # 1-3
    started_at: datetime
    ended_at: datetime | None = None
    total_exercises: int
    correct_count: int
    duration_seconds: int | None = None

    model_config = ConfigDict(from_attributes=True)


class ExerciseAttemptOut(BaseModel):
    """A single exercise attempt within a session."""
    id: UUID
    exercise_type: ExerciseType
    word_id: UUID | None = None
    chunk_id: UUID | None = None
    root_id: UUID | None = None
    surah_number: int | None = None
    verse_number: int | None = None
    is_correct: bool
    response_time_ms: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ─── Request Schemas (Create/Update) ─────────────────────────────────────────


class ReviewCardRequest(BaseModel):
    """Request to review a Leitner card."""
    card_id: UUID
    is_correct: bool


class ExerciseAttemptCreate(BaseModel):
    """Request to record an exercise attempt."""
    session_id: UUID
    exercise_type: str  # ExerciseType value
    word_id: UUID | None = None
    chunk_id: UUID | None = None
    root_id: UUID | None = None
    surah_number: int | None = None
    verse_number: int | None = None
    is_correct: bool
    response_time_ms: int | None = None
    shown_data: dict | None = None  # What was presented to the student
    answer_data: dict | None = None  # What the student answered


class StartSessionRequest(BaseModel):
    """Request to start a new exercise session."""
    module: int = Field(ge=1, le=5)  # 1-5
    phase: int = Field(ge=1, le=3)   # 1-3


class FlashRecallExercise(BaseModel):
    """A generated flash recall / QCM exercise."""
    word_id: UUID
    choices: list[QuranWordOut] = Field(min_length=2, max_length=4)
    correct_index: int  # Index into choices list


class VerseScanResult(BaseModel):
    """Result of a verse scan exercise (word recognition in context)."""
    surah_number: int
    verse_number: int
    recognized_word_ids: list[UUID]  # Words the student correctly identified
    total_words: int  # Total words in the verse
    recognized_count: int  # Count of recognized words
    coverage_percent: float  # (recognized_count / total_words) * 100
