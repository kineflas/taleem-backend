"""
Médine Tome 1 — V2 Router
Serves pre-generated lesson content from lessons_content_v2.json
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.medine_v2 import (
    LessonContentV2,
    LessonListItemV2,
    LessonProgressV2,
    ProgressUpdateV2,
    QuizResultV2,
    QuizSubmitV2,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2", tags=["Médine V2"])

# ── Load static content at module level ──────────────────────────────────────

_CONTENT_PATH = Path(__file__).resolve().parent.parent / "data" / "lessons_content_v2.json"
_LESSONS: dict[str, dict] = {}

if _CONTENT_PATH.exists():
    with open(_CONTENT_PATH, encoding="utf-8") as f:
        _LESSONS = json.load(f)
    logger.info("Médine V2: loaded %d lessons from %s", len(_LESSONS), _CONTENT_PATH.name)
else:
    logger.warning("Médine V2: %s not found — endpoints will return empty data", _CONTENT_PATH)

# In-memory progress store (per-session; will be replaced by DB later)
_PROGRESS: dict[str, LessonProgressV2] = {}


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/lessons", response_model=list[LessonListItemV2])
def list_lessons_v2():
    """List all 23 lessons with unlock status."""
    items = []
    for key in sorted(_LESSONS.keys(), key=int):
        lesson = _LESSONS[key]
        ln = lesson["lesson_number"]
        progress = _PROGRESS.get(str(ln))

        # Unlock logic: lesson 1 always open, others need previous lesson completed
        is_unlocked = ln == 1
        if ln > 1:
            prev = _PROGRESS.get(str(ln - 1))
            if prev and prev.stars >= 1:
                is_unlocked = True

        items.append(LessonListItemV2(
            lesson_number=ln,
            title_fr=lesson["title_fr"],
            title_ar=lesson.get("title_ar"),
            part_number=lesson["part_number"],
            part_name=lesson["part_name"],
            stars=progress.stars if progress else 0,
            is_completed=progress.is_completed if progress else False,
            is_unlocked=is_unlocked,
        ))
    return items


@router.get("/lessons/{lesson_number}", response_model=LessonContentV2)
def get_lesson_v2(lesson_number: int):
    """Get full V2 content for a lesson."""
    lesson = _LESSONS.get(str(lesson_number))
    if not lesson:
        raise HTTPException(status_code=404, detail=f"Lesson {lesson_number} not found")
    return LessonContentV2(**lesson)


@router.post("/lessons/{lesson_number}/progress", response_model=LessonProgressV2)
def update_progress_v2(lesson_number: int, body: ProgressUpdateV2):
    """Update progress for a lesson step."""
    key = str(lesson_number)
    if key not in _LESSONS:
        raise HTTPException(status_code=404, detail=f"Lesson {lesson_number} not found")

    progress = _PROGRESS.get(key, LessonProgressV2())

    step_map = {
        "discovery": "discovery_done",
        "dialogue": "dialogue_done",
        "exercises": "exercises_score",
        "quiz": "quiz_score",
    }

    field = step_map.get(body.step)
    if not field:
        raise HTTPException(status_code=400, detail=f"Unknown step: {body.step}")

    if field in ("discovery_done", "dialogue_done"):
        setattr(progress, field, True)
    else:
        setattr(progress, field, body.value)

    # Calculate completion
    steps_done = sum([
        progress.discovery_done,
        progress.dialogue_done,
        (progress.exercises_score or 0) > 0,
        (progress.quiz_score or 0) > 0,
    ])
    progress.current_step = steps_done

    # Stars based on quiz score
    if progress.quiz_score is not None and progress.quiz_score > 0:
        if progress.quiz_score >= 85:
            progress.stars = 3
        elif progress.quiz_score >= 60:
            progress.stars = 2
        else:
            progress.stars = 1
        progress.is_completed = True

    _PROGRESS[key] = progress
    return progress


@router.post("/lessons/{lesson_number}/quiz/submit", response_model=QuizResultV2)
def submit_quiz_v2(lesson_number: int, body: QuizSubmitV2):
    """Submit quiz answers and return scored result."""
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

        # Find question
        question = next((q for q in quiz_questions if q["id"] == q_id), None)
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

    # XP: base 5 per question + bonus for speed
    xp = correct_count * 5
    if body.time_ms > 0 and body.time_ms < total * 5000:  # < 5s per question
        xp += total * 2  # speed bonus

    # Update progress
    progress = _PROGRESS.get(key, LessonProgressV2())
    progress.quiz_score = score
    progress.stars = max(progress.stars, stars)
    progress.is_completed = True
    progress.xp_earned += xp
    _PROGRESS[key] = progress

    return QuizResultV2(
        score=score,
        total=total,
        correct=correct_count,
        stars=stars,
        xp_earned=xp,
        results=results,
    )
