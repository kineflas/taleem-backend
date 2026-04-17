"""Pydantic schemas for L'Odyssée des Lettres module."""
from __future__ import annotations

from pydantic import BaseModel, field_validator


# ── Letter Data ─────────────────────────────────────────────────────────────

class SyllabeInfo(BaseModel):
    glyph: str
    son: str
    audio_id: str


class FormesPositionnelles(BaseModel):
    isolee: str
    debut: str
    milieu: str
    fin: str


class LetterData(BaseModel):
    id: str
    glyph: str
    name_fr: str
    name_ar: str
    mnemonique_visuelle: str
    conseil_anatomique: str
    audio_id: str
    famille: str
    connectante: bool
    formes_positionnelles: FormesPositionnelles
    syllabes: dict[str, SyllabeInfo]  # fatha, damma, kasra


# ── Écoute ──────────────────────────────────────────────────────────────────

class EcouteSequenceItem(BaseModel):
    audio_id: str
    label: str


class AnatomieItem(BaseModel):
    lettre_id: str
    zone: str
    description: str


class EcouteData(BaseModel):
    instruction: str
    sequence: list[EcouteSequenceItem] = []
    anatomie: list[AnatomieItem] = []


# ── Mini-lecture (Karaoké) ──────────────────────────────────────────────────

class KaraokeItem(BaseModel):
    text: str
    son: str
    audio_id: str
    delay_ms: int = 0


class MiniLectureData(BaseModel):
    type: str  # KARAOKE
    instruction: str
    items: list[KaraokeItem] = []


# ── Exercise Items (per type) ──────────────────────────────────────────────

class FusionItem(BaseModel):
    lettre: str
    haraka: str
    haraka_nom: str
    resultat: str
    son: str
    audio_id: str


class PointsItem(BaseModel):
    forme_base: str
    cible: str
    nom_cible: str
    points: int
    position: str


class AudioQuizItem(BaseModel):
    audio_id: str
    son: str
    options: list[str]
    correct: int


class CompleterSyllabeItem(BaseModel):
    lettre: str
    son_cible: str
    options: list[str]
    correct: int


class CameleonItem(BaseModel):
    lettre: str
    position: str
    options: list[str]
    correct: int


class EcouteComparativeItem(BaseModel):
    audio_id: str
    label: str
    question: str
    options: list[str]
    correct: int


class ClassifierItem(BaseModel):
    word: str
    category: str


class MurInvisibleItem(BaseModel):
    lettre: str
    connectante: bool
    animation: str


class ThermometreItem(BaseModel):
    audio_id: str
    lettre: str
    zone_correcte: str
    profondeur: float
    label: str


class SpeedRoundItem(BaseModel):
    glyph: str
    name: str


class DicteeItem(BaseModel):
    audio_id: str
    mot: str
    syllabes_correctes: list[str]
    distracteurs: list[str]


# ── Unified Exercise ───────────────────────────────────────────────────────

class OdysseeExercise(BaseModel):
    """Polymorphic exercise — `type` determines which fields are populated."""
    type: str  # FUSION, POINTS, AUDIO_QUIZ, COMPLETER_SYLLABE, CAMELEON,
               # ECOUTE_COMPARATIVE, CLASSIFIER, MUR_INVISIBLE, THERMOMETRE,
               # SPEED_ROUND, DICTEE, KARAOKE
    prompt_fr: str | None = None
    items: list[dict] | None = None          # generic items list
    categories: list[str] | None = None      # CLASSIFIER
    time_limit_seconds: int | None = None    # SPEED_ROUND


# ── Quiz ───────────────────────────────────────────────────────────────────

class OdysseeQuizQuestion(BaseModel):
    id: str
    question: str
    options: list[str]
    correct: int
    explanation: str | None = None

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id_to_str(cls, v: object) -> str:
        return str(v)


# ── Flashcards ─────────────────────────────────────────────────────────────

class OdysseeFlashcard(BaseModel):
    id: str | None = None
    front_ar: str
    back_fr: str
    category: str | None = None
    example_ar: str | None = None
    example_fr: str | None = None

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id_to_str(cls, v: object) -> str | None:
        return str(v) if v is not None else None


# ── Lesson Content ─────────────────────────────────────────────────────────

class OdysseeLessonContent(BaseModel):
    lesson_number: int
    title_fr: str
    title_ar: str | None = None
    phase_number: int
    phase_name: str
    objective: str | None = None
    letters: list[LetterData] = []
    ecoute: EcouteData | None = None
    exercises: list[OdysseeExercise] = []
    mini_lecture: MiniLectureData | None = None
    quiz_questions: list[OdysseeQuizQuestion] = []
    flashcards: list[OdysseeFlashcard] = []


# ── List Item ──────────────────────────────────────────────────────────────

class OdysseeLessonListItem(BaseModel):
    lesson_number: int
    title_fr: str
    title_ar: str | None = None
    phase_number: int
    phase_name: str
    stars: int = 0
    is_completed: bool = False
    is_unlocked: bool = True


# ── Progress ───────────────────────────────────────────────────────────────

class OdysseeLessonProgress(BaseModel):
    current_step: int = 0
    ecoute_done: bool = False
    discovery_done: bool = False
    exercises_score: float | None = None
    mini_lecture_done: bool = False
    quiz_score: float | None = None
    stars: int = 0
    is_completed: bool = False
    xp_earned: int = 0


class OdysseeProgressUpdate(BaseModel):
    step: str  # ecoute, discovery, exercises, mini_lecture, quiz
    value: float = 1.0


class OdysseeQuizSubmit(BaseModel):
    answers: list[dict]
    time_ms: int = 0


class OdysseeQuizResult(BaseModel):
    score: float
    total: int
    correct: int
    stars: int
    xp_earned: int
    results: list[dict] = []


# ── Boss Quiz (per phase) ─────────────────────────────────────────────────

class OdysseeBossQuizContent(BaseModel):
    phase_number: int
    title: str
    lessons_covered: list[int]
    time_limit: int = 15
    passing_score: int = 70
    questions: list[OdysseeQuizQuestion]


class OdysseeBossQuizResult(BaseModel):
    score: float
    total: int
    correct: int
    stars: int
    xp_earned: int
    passed: bool
    results: list[dict] = []


# ── Stats ──────────────────────────────────────────────────────────────────

class OdysseeStats(BaseModel):
    total_lessons: int
    completed_lessons: int
    total_stars: int
    total_xp: int
    letters_learned: int
    current_phase: int
