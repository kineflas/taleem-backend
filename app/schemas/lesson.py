"""Pydantic schemas for the Lesson detail API."""
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class TheorySection(BaseModel):
    """A section within the theory content."""
    title_fr: str
    content_fr: str
    content_ar: Optional[str] = None
    tip_fr: Optional[str] = None


class ExampleItem(BaseModel):
    """An example showing practical usage."""
    arabic: str
    transliteration: Optional[str] = None
    translation_fr: str
    breakdown_fr: Optional[str] = None
    grammatical_note_fr: Optional[str] = None


class VocabItem(BaseModel):
    """A vocabulary entry."""
    arabic: str
    translation_fr: str
    transliteration: Optional[str] = None


class IllustrationItem(BaseModel):
    """A visual illustration (table, diagram, etc)."""
    type: str  # "table" or "diagram"
    title_fr: str
    data: Optional[dict | str] = None


class QuizQuestion(BaseModel):
    """A single quiz question."""
    id: str
    question: str
    options: list[str]
    correct: int
    explanation: Optional[str] = None


class DialogueLine(BaseModel):
    """A single line of dialogue."""
    speaker_ar: str
    arabic: str
    french: str = ""


class DialogueContent(BaseModel):
    """Structured dialogue with optional situation context."""
    situation: Optional[str] = None
    lines: list[DialogueLine] = []


class LessonTheory(BaseModel):
    """Aggregated theory content for a lesson."""
    sections: list[TheorySection] = []
    examples: list[ExampleItem] = []
    vocab: list[VocabItem] = []
    illustrations: list[IllustrationItem] = []
    grammar_summary: Optional[str] = None
    # Rich prose fields from the MD parser
    objective: Optional[str] = None
    coin_experts: Optional[str] = None
    dialogue: Optional[DialogueContent] = None
    mise_en_situation: Optional[str] = None
    exercises_md: Optional[str] = None
    pronunciation: Optional[str] = None


class LessonProgress(BaseModel):
    """Student's progress on a lesson."""
    theory_completed: bool = False
    dialogue_completed: bool = False
    exercises_score: Optional[float] = None
    quiz_score: Optional[float] = None
    stars: int = 0  # 0-3
    is_completed: bool = False


class LessonDetailResponse(BaseModel):
    """Full lesson detail with content and student progress."""
    unit_id: UUID
    lesson_number: int
    part_number: int
    title_ar: str
    title_fr: str
    description_fr: Optional[str] = None
    theory: LessonTheory
    quiz_questions: list[QuizQuestion] = []
    quiz_md_questions: list[QuizQuestion] = []  # Additional questions from the MD
    is_unlocked: bool = True
    previous_lesson_stars: int = 0
    progress: Optional[LessonProgress] = None

    model_config = {"from_attributes": True}


class LessonListItem(BaseModel):
    """Lesson summary for list view."""
    unit_id: UUID
    lesson_number: int
    title_ar: str
    title_fr: str
    stars: int = 0
    is_completed: bool = False
    is_unlocked: bool = True
    is_mastered_by_diagnostic: bool = False


class LessonProgressUpdate(BaseModel):
    """Request to update progress on a segment."""
    segment: str  # "theory", "dialogue", "exercises", "quiz"
    value: float  # 0.0 to 1.0


class QuizSubmission(BaseModel):
    """Submit quiz answers."""
    answers: list[dict]  # [{question_id: str, selected: int}]
    time_ms: int = 0


class QuizResultResponse(BaseModel):
    """Results after quiz submission."""
    score: float
    total: int
    correct: int
    stars: int  # 1-3
    xp_earned: int
    results: list[dict]  # [{question_id, selected, correct, is_correct}]
