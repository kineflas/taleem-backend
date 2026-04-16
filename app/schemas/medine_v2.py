"""Pydantic schemas for Médine Tome 1 — V2 module."""
from __future__ import annotations

from pydantic import BaseModel


# ── Discovery Cards ──────────────────────────────────────────────────────────

class DiscoveryCardExample(BaseModel):
    ar: str
    fr: str
    translit: str | None = None


class DiscoveryCard(BaseModel):
    type: str  # rule, expert_corner, pronunciation, examples_table, mise_en_situation
    title_fr: str | None = None
    content_fr: str | None = None
    content_ar: str | None = None
    examples: list[DiscoveryCardExample] | None = None
    items: list[dict] | None = None   # pronunciation items
    rows: list[dict] | None = None    # examples_table rows


# ── Dialogue ─────────────────────────────────────────────────────────────────

class DialogueLineV2(BaseModel):
    speaker_ar: str
    arabic: str
    french: str = ""


class DialogueV2(BaseModel):
    situation: str | None = None
    lines: list[DialogueLineV2] = []


# ── Exercises ────────────────────────────────────────────────────────────────

class ExerciseItem(BaseModel):
    sentence: str | None = None
    answer: str | None = None
    prompt_fr: str | None = None
    answer_ar: str | None = None
    word: str | None = None
    category: str | None = None


class ExerciseV2(BaseModel):
    type: str  # REORDER, FILL_BLANK, TRANSLATE, CLASSIFY
    prompt_fr: str | None = None
    words: list[str] | None = None
    answer: list[str] | None = None
    items: list[ExerciseItem] | None = None
    categories: list[str] | None = None


# ── Quiz ─────────────────────────────────────────────────────────────────────

class QuizQuestionV2(BaseModel):
    id: str
    question: str
    options: list[str]
    correct: int
    explanation: str | None = None


# ── Flashcards ───────────────────────────────────────────────────────────────

class FlashcardV2(BaseModel):
    id: str | None = None
    front_ar: str
    back_fr: str
    category: str | None = None
    example_ar: str | None = None
    example_fr: str | None = None


# ── Lesson Content ───────────────────────────────────────────────────────────

class LessonContentV2(BaseModel):
    lesson_number: int
    title_fr: str
    title_ar: str | None = None
    part_number: int
    part_name: str
    objective: str | None = None
    discovery_cards: list[DiscoveryCard] = []
    dialogue: DialogueV2 | None = None
    exercises: list[ExerciseV2] = []
    quiz_questions: list[QuizQuestionV2] = []
    flashcards: list[FlashcardV2] = []


# ── List Item ────────────────────────────────────────────────────────────────

class LessonListItemV2(BaseModel):
    lesson_number: int
    title_fr: str
    title_ar: str | None = None
    part_number: int
    part_name: str
    stars: int = 0
    is_completed: bool = False
    is_unlocked: bool = True


# ── Progress ─────────────────────────────────────────────────────────────────

class LessonProgressV2(BaseModel):
    current_step: int = 0
    discovery_done: bool = False
    dialogue_done: bool = False
    exercises_score: float | None = None
    quiz_score: float | None = None
    stars: int = 0
    is_completed: bool = False
    xp_earned: int = 0


class ProgressUpdateV2(BaseModel):
    step: str  # discovery, dialogue, exercises, quiz
    value: float = 1.0


class QuizSubmitV2(BaseModel):
    answers: list[dict]
    time_ms: int = 0


class QuizResultV2(BaseModel):
    score: float
    total: int
    correct: int
    stars: int
    xp_earned: int
    results: list[dict] = []


# ── Boss Quiz ───────────────────────────────────────────────────────────────

class BossQuizQuestion(BaseModel):
    id: str
    question: str
    options: list[str]
    correct: int
    explanation: str | None = None


class BossQuizContent(BaseModel):
    part_number: int
    title: str
    lessons_covered: list[int]
    time_limit: int = 15
    passing_score: int = 70
    questions: list[BossQuizQuestion]


class BossQuizResult(BaseModel):
    score: float
    total: int
    correct: int
    stars: int
    xp_earned: int
    passed: bool
    results: list[dict] = []


# ── Final Exam ──────────────────────────────────────────────────────────────

class FinalExamContent(BaseModel):
    exam_title: str
    time_limit: int
    passing_score: int
    total_questions: int
    questions: list[BossQuizQuestion]


class FinalExamResult(BaseModel):
    score: float
    total: int
    correct: int
    stars: int
    xp_earned: int
    passed: bool
    results: list[dict] = []


# ── Diagnostic CAT ──────────────────────────────────────────────────────────

class DiagnosticQuestion(BaseModel):
    id: str
    lesson_target: str
    difficulty: int
    skill_tested: str
    question: str
    options: list[str]
    correct: int
    explanation: str | None = None
    adaptive_hint: str | None = None


class DiagnosticContent(BaseModel):
    test_name: str
    total_questions: int
    estimated_time: str
    questions: list[DiagnosticQuestion]


class DiagnosticSubmit(BaseModel):
    answers: list[dict]  # [{"question_id": "Q1", "selected": 0}, ...]
    time_ms: int = 0


class CompetencyScore(BaseModel):
    id: str
    name: str
    score: float  # 0.0 to 1.0


class DiagnosticResult(BaseModel):
    score: float
    total: int
    correct: int
    level: str
    start_at_lesson: int
    start_at_part: int
    message: str
    competencies: list[CompetencyScore] = []
    results: list[dict] = []
