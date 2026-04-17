"""
L'Odyssée des Lettres — Router
Serves pre-generated Arabic alphabet lesson content + persists progress per-student.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.dependencies import CurrentUser, DB
from ..database import get_db
from ..models.odyssee_lettres import OdysseeProgress
from ..models.user import User
from ..schemas.odyssee_lettres import (
    OdysseeBossQuizContent,
    OdysseeBossQuizResult,
    OdysseeLessonContent,
    OdysseeLessonListItem,
    OdysseeLessonProgress,
    OdysseeProgressUpdate,
    OdysseeQuizResult,
    OdysseeQuizSubmit,
    OdysseeStats,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/odyssee", tags=["Odyssée des Lettres"])

# ── Load static content at module level ──────────────────────────────────────

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_CONTENT_PATH = _DATA_DIR / "odyssee_lettres.json"

_LESSONS: dict[str, dict] = {}

if _CONTENT_PATH.exists():
    with open(_CONTENT_PATH, encoding="utf-8") as f:
        _LESSONS = json.load(f)
    logger.info(
        "Odyssée des Lettres: loaded %d lessons from %s",
        len(_LESSONS), _CONTENT_PATH.name,
    )
else:
    logger.warning(
        "Odyssée des Lettres: %s not found — endpoints will return empty data",
        _CONTENT_PATH,
    )

# Phase metadata
_PHASES = {
    1: {"name": "Les Familières", "lessons": list(range(1, 6))},
    2: {"name": "Les Nouvelles", "lessons": list(range(6, 11))},
    3: {"name": "Les Profondes", "lessons": list(range(11, 16))},
    4: {"name": "Le Grand Voyage", "lessons": list(range(16, 19))},
}

# Total letters in the programme (28 base + alif = 29 entries)
_TOTAL_LETTERS = 29


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_or_create_progress(
    db: Session, student_id, lesson_number: int,
) -> OdysseeProgress:
    """Fetch existing progress or create a new empty row."""
    progress = db.query(OdysseeProgress).filter_by(
        student_id=student_id,
        lesson_number=lesson_number,
    ).first()
    if not progress:
        progress = OdysseeProgress(
            student_id=student_id,
            lesson_number=lesson_number,
        )
        db.add(progress)
        db.flush()
    return progress


def _progress_to_schema(p: OdysseeProgress | None) -> OdysseeLessonProgress:
    """Convert DB row to Pydantic schema (or default if None)."""
    if p is None:
        return OdysseeLessonProgress()
    return OdysseeLessonProgress(
        current_step=p.current_step,
        ecoute_done=p.ecoute_done,
        discovery_done=p.discovery_done,
        exercises_score=p.exercises_score,
        mini_lecture_done=p.mini_lecture_done,
        quiz_score=p.quiz_score,
        stars=p.stars,
        is_completed=p.is_completed,
        xp_earned=p.xp_earned,
    )


def _update_xp_on_user(db: Session, user: User, xp: int) -> None:
    """Add XP to user's total and recalculate level."""
    user.total_xp = (user.total_xp or 0) + xp
    user.level = 1 + user.total_xp // 100
    db.flush()


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/lessons", response_model=list[OdysseeLessonListItem])
def list_odyssee_lessons(current_user: CurrentUser, db: DB):
    """List all 18 Odyssée lessons with unlock status."""
    all_progress = db.query(OdysseeProgress).filter_by(
        student_id=current_user.id,
    ).all()
    progress_map: dict[int, OdysseeProgress] = {
        p.lesson_number: p for p in all_progress
    }

    items = []
    for key in sorted(_LESSONS.keys(), key=int):
        lesson = _LESSONS[key]
        ln = lesson["lesson_number"]
        progress = progress_map.get(ln)

        # Unlock logic: lesson 1 always open, others need previous lesson stars >= 1
        is_unlocked = ln == 1
        if ln > 1:
            prev = progress_map.get(ln - 1)
            if prev and prev.stars >= 1:
                is_unlocked = True

        items.append(OdysseeLessonListItem(
            lesson_number=ln,
            title_fr=lesson["title_fr"],
            title_ar=lesson.get("title_ar"),
            phase_number=lesson["phase_number"],
            phase_name=lesson["phase_name"],
            stars=progress.stars if progress else 0,
            is_completed=progress.is_completed if progress else False,
            is_unlocked=is_unlocked,
        ))
    return items


@router.get("/lessons/{lesson_number}", response_model=OdysseeLessonContent)
def get_odyssee_lesson(lesson_number: int, current_user: CurrentUser):
    """Get full content for an Odyssée lesson."""
    lesson = _LESSONS.get(str(lesson_number))
    if not lesson:
        raise HTTPException(status_code=404, detail=f"Lesson {lesson_number} not found")
    return OdysseeLessonContent(**lesson)


@router.get(
    "/lessons/{lesson_number}/progress",
    response_model=OdysseeLessonProgress,
)
def get_odyssee_progress(lesson_number: int, current_user: CurrentUser, db: DB):
    """Get current progress for a specific lesson."""
    progress = db.query(OdysseeProgress).filter_by(
        student_id=current_user.id,
        lesson_number=lesson_number,
    ).first()
    return _progress_to_schema(progress)


@router.post(
    "/lessons/{lesson_number}/progress",
    response_model=OdysseeLessonProgress,
)
def update_odyssee_progress(
    lesson_number: int,
    body: OdysseeProgressUpdate,
    current_user: CurrentUser,
    db: DB,
):
    """Update progress for a lesson step (persisted to DB)."""
    if str(lesson_number) not in _LESSONS:
        raise HTTPException(status_code=404, detail=f"Lesson {lesson_number} not found")

    progress = _get_or_create_progress(db, current_user.id, lesson_number)

    step_map = {
        "ecoute": "ecoute_done",
        "discovery": "discovery_done",
        "exercises": "exercises_score",
        "mini_lecture": "mini_lecture_done",
        "quiz": "quiz_score",
    }

    field = step_map.get(body.step)
    if not field:
        raise HTTPException(status_code=400, detail=f"Unknown step: {body.step}")

    if field.endswith("_done"):
        setattr(progress, field, True)
    else:
        setattr(progress, field, body.value)

    # Calculate completion (5 steps in the 7-step flow: écoute, découverte,
    # exercices, mini-lecture, quiz — objectif and résultat are UI-only)
    steps_done = sum([
        progress.ecoute_done,
        progress.discovery_done,
        (progress.exercises_score or 0) > 0,
        progress.mini_lecture_done,
        (progress.quiz_score or 0) > 0,
    ])
    progress.current_step = steps_done

    # Stars based on quiz score
    if progress.quiz_score is not None and progress.quiz_score > 0:
        if progress.quiz_score >= 85:
            progress.stars = max(progress.stars, 3)
        elif progress.quiz_score >= 60:
            progress.stars = max(progress.stars, 2)
        else:
            progress.stars = max(progress.stars, 1)
        progress.is_completed = True

    progress.updated_at = datetime.now(timezone.utc)
    db.commit()
    return _progress_to_schema(progress)


@router.post(
    "/lessons/{lesson_number}/quiz/submit",
    response_model=OdysseeQuizResult,
)
def submit_odyssee_quiz(
    lesson_number: int,
    body: OdysseeQuizSubmit,
    current_user: CurrentUser,
    db: DB,
):
    """Submit quiz answers and return scored result (persisted to DB)."""
    key = str(lesson_number)
    lesson = _LESSONS.get(key)
    if not lesson:
        raise HTTPException(status_code=404, detail=f"Lesson {lesson_number} not found")

    quiz_questions = lesson.get("quiz_questions", [])
    total = len(quiz_questions)
    if total == 0:
        raise HTTPException(status_code=400, detail="No quiz questions for this lesson")

    # Score answers
    correct_count = 0
    results = []
    for ans in body.answers:
        q_id = ans.get("question_id", "")
        selected = ans.get("selected", -1)

        question = None
        for q in quiz_questions:
            if str(q["id"]) == str(q_id):
                question = q
                break

        if question:
            is_correct = selected == question["correct"]
            if is_correct:
                correct_count += 1
            results.append({
                "question_id": q_id,
                "selected": selected,
                "correct": question["correct"],
                "is_correct": is_correct,
                "explanation": question.get("explanation"),
            })

    score = (correct_count / total * 100) if total > 0 else 0

    # Stars
    if score >= 85:
        stars = 3
    elif score >= 60:
        stars = 2
    else:
        stars = 1

    # XP: base 5 per correct + speed bonus
    xp = correct_count * 5
    if body.time_ms > 0 and body.time_ms < total * 5000:
        xp += total * 2

    # Persist progress
    progress = _get_or_create_progress(db, current_user.id, lesson_number)
    progress.quiz_score = score
    progress.stars = max(progress.stars, stars)
    progress.is_completed = True
    progress.xp_earned = (progress.xp_earned or 0) + xp
    progress.updated_at = datetime.now(timezone.utc)

    # Update user's total XP
    _update_xp_on_user(db, current_user, xp)

    db.commit()

    return OdysseeQuizResult(
        score=score,
        total=total,
        correct=correct_count,
        stars=stars,
        xp_earned=xp,
        results=results,
    )


# ── Flashcard endpoints ─────────────────────────────────────────────────────

@router.get("/flashcards", response_model=list[dict])
def get_odyssee_flashcards(current_user: CurrentUser, db: DB):
    """Return all flashcards from completed Odyssée lessons for review."""
    completed = db.query(OdysseeProgress).filter_by(
        student_id=current_user.id,
        is_completed=True,
    ).all()
    completed_numbers = {p.lesson_number for p in completed}

    all_flashcards = []
    for ln in sorted(completed_numbers):
        lesson = _LESSONS.get(str(ln))
        if not lesson:
            continue
        cards = lesson.get("flashcards", [])
        if cards:
            all_flashcards.append({
                "lesson_number": ln,
                "title_fr": lesson["title_fr"],
                "phase_number": lesson["phase_number"],
                "cards": cards,
            })
    return all_flashcards


# ── Stats ───────────────────────────────────────────────────────────────────

@router.get("/stats", response_model=OdysseeStats)
def get_odyssee_stats(current_user: CurrentUser, db: DB):
    """Return aggregated student stats for the Odyssée module."""
    all_progress = db.query(OdysseeProgress).filter_by(
        student_id=current_user.id,
    ).all()

    completed = [p for p in all_progress if p.is_completed]
    total_stars = sum(p.stars for p in all_progress)
    total_xp = sum(p.xp_earned for p in all_progress)

    # Count distinct letters learned from completed lessons
    letters_learned = set()
    for p in completed:
        lesson = _LESSONS.get(str(p.lesson_number))
        if lesson:
            for letter in lesson.get("letters", []):
                letters_learned.add(letter["id"])

    # Current phase: highest phase with at least 1 lesson started
    current_phase = 1
    for p in all_progress:
        lesson = _LESSONS.get(str(p.lesson_number))
        if lesson:
            current_phase = max(current_phase, lesson["phase_number"])

    return OdysseeStats(
        total_lessons=len(_LESSONS),
        completed_lessons=len(completed),
        total_stars=total_stars,
        total_xp=total_xp,
        letters_learned=len(letters_learned),
        current_phase=current_phase,
    )


# ── Letter reference endpoint ──────────────────────────────────────────────

@router.get("/letters", response_model=list[dict])
def get_all_letters(current_user: CurrentUser):
    """Return all letter data from all lessons (alphabet reference)."""
    seen = set()
    letters = []
    for key in sorted(_LESSONS.keys(), key=int):
        for letter in _LESSONS[key].get("letters", []):
            if letter["id"] not in seen:
                seen.add(letter["id"])
                letters.append(letter)
    return letters


@router.get("/letters/{letter_id}", response_model=dict)
def get_letter_detail(letter_id: str, current_user: CurrentUser):
    """Return detailed data for a specific letter."""
    for key in sorted(_LESSONS.keys(), key=int):
        for letter in _LESSONS[key].get("letters", []):
            if letter["id"] == letter_id:
                return letter
    raise HTTPException(status_code=404, detail=f"Letter '{letter_id}' not found")


# ── Phase boss quiz (cumulative per phase) ────────────────────────────────

@router.get("/phases/{phase_number}/quiz", response_model=OdysseeBossQuizContent)
def get_phase_boss_quiz(phase_number: int, current_user: CurrentUser):
    """Generate a boss quiz from all quiz questions in the given phase."""
    phase = _PHASES.get(phase_number)
    if not phase:
        raise HTTPException(status_code=404, detail=f"Phase {phase_number} not found")

    # Collect all quiz questions from lessons in this phase
    questions = []
    for ln in phase["lessons"]:
        lesson = _LESSONS.get(str(ln))
        if lesson:
            questions.extend(lesson.get("quiz_questions", []))

    if not questions:
        raise HTTPException(
            status_code=400,
            detail=f"No quiz questions available for phase {phase_number}",
        )

    return OdysseeBossQuizContent(
        phase_number=phase_number,
        title=f"Boss Quiz — {phase['name']}",
        lessons_covered=phase["lessons"],
        time_limit=max(10, len(questions)),  # ~1 min per question
        passing_score=70,
        questions=questions,
    )


@router.post(
    "/phases/{phase_number}/quiz/submit",
    response_model=OdysseeBossQuizResult,
)
def submit_phase_boss_quiz(
    phase_number: int,
    body: OdysseeQuizSubmit,
    current_user: CurrentUser,
    db: DB,
):
    """Submit phase boss quiz answers and return scored result."""
    phase = _PHASES.get(phase_number)
    if not phase:
        raise HTTPException(status_code=404, detail=f"Phase {phase_number} not found")

    # Collect all quiz questions
    questions = []
    for ln in phase["lessons"]:
        lesson = _LESSONS.get(str(ln))
        if lesson:
            questions.extend(lesson.get("quiz_questions", []))

    total = len(questions)
    if total == 0:
        raise HTTPException(status_code=400, detail="No questions for this phase")

    correct_count = 0
    results = []
    for ans in body.answers:
        q_id = str(ans.get("question_id", ""))
        selected = ans.get("selected", -1)

        question = None
        for q in questions:
            if str(q["id"]) == q_id:
                question = q
                break

        if question:
            is_correct = selected == question["correct"]
            if is_correct:
                correct_count += 1
            results.append({
                "question_id": q_id,
                "selected": selected,
                "correct": question["correct"],
                "is_correct": is_correct,
                "explanation": question.get("explanation"),
            })

    score = (correct_count / total * 100) if total > 0 else 0
    passed = score >= 70

    if score >= 85:
        stars = 3
    elif score >= 60:
        stars = 2
    else:
        stars = 1

    xp = correct_count * 8
    if passed:
        xp += 20

    _update_xp_on_user(db, current_user, xp)
    db.commit()

    return OdysseeBossQuizResult(
        score=score,
        total=total,
        correct=correct_count,
        stars=stars,
        xp_earned=xp,
        passed=passed,
        results=results,
    )
