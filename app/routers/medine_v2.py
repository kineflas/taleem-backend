"""
Médine Tome 1 — V2 Router
Serves pre-generated lesson content + persists progress per-student in PostgreSQL.
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
from ..models.medine_v2 import MedineV2Progress
from ..models.user import User
from ..schemas.medine_v2 import (
    BossQuizContent,
    BossQuizResult,
    CompetencyScore,
    DiagnosticContent,
    DiagnosticResult,
    DiagnosticSubmit,
    FinalExamContent,
    FinalExamResult,
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

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_CONTENT_PATH = _DATA_DIR / "lessons_content_v2.json"
_BOSS_QUIZZES_PATH = _DATA_DIR / "boss_quizzes_v2.json"
_FINAL_EXAM_PATH = _DATA_DIR / "final_exam_v2.json"
_DIAGNOSTIC_PATH = _DATA_DIR / "diagnostic_v2.json"

_LESSONS: dict[str, dict] = {}
_BOSS_QUIZZES: dict[str, dict] = {}
_FINAL_EXAM: dict = {}
_DIAGNOSTIC: dict = {}

if _CONTENT_PATH.exists():
    with open(_CONTENT_PATH, encoding="utf-8") as f:
        _LESSONS = json.load(f)
    logger.info("Médine V2: loaded %d lessons from %s", len(_LESSONS), _CONTENT_PATH.name)
else:
    logger.warning("Médine V2: %s not found — endpoints will return empty data", _CONTENT_PATH)

if _BOSS_QUIZZES_PATH.exists():
    with open(_BOSS_QUIZZES_PATH, encoding="utf-8") as f:
        _BOSS_QUIZZES = json.load(f).get("parts", {})
    logger.info("Médine V2: loaded %d boss quizzes", len(_BOSS_QUIZZES))

if _FINAL_EXAM_PATH.exists():
    with open(_FINAL_EXAM_PATH, encoding="utf-8") as f:
        _FINAL_EXAM = json.load(f)
    logger.info("Médine V2: loaded final exam (%d questions)", len(_FINAL_EXAM.get("questions", [])))

if _DIAGNOSTIC_PATH.exists():
    with open(_DIAGNOSTIC_PATH, encoding="utf-8") as f:
        _DIAGNOSTIC = json.load(f)
    logger.info("Médine V2: loaded diagnostic test (%d questions)", len(_DIAGNOSTIC.get("questions", [])))


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_or_create_progress(
    db: Session, student_id, lesson_number: int,
) -> MedineV2Progress:
    """Fetch existing progress or create a new empty row."""
    progress = db.query(MedineV2Progress).filter_by(
        student_id=student_id,
        lesson_number=lesson_number,
    ).first()
    if not progress:
        progress = MedineV2Progress(
            student_id=student_id,
            lesson_number=lesson_number,
        )
        db.add(progress)
        db.flush()
    return progress


def _progress_to_schema(p: MedineV2Progress | None) -> LessonProgressV2:
    """Convert DB row to Pydantic schema (or default if None)."""
    if p is None:
        return LessonProgressV2()
    return LessonProgressV2(
        current_step=p.current_step,
        discovery_done=p.discovery_done,
        dialogue_done=p.dialogue_done,
        exercises_score=p.exercises_score,
        quiz_score=p.quiz_score,
        stars=p.stars,
        is_completed=p.is_completed,
        xp_earned=p.xp_earned,
    )


def _update_xp_on_user(db: Session, user: User, xp: int) -> None:
    """Add XP to user's total and recalculate level."""
    user.total_xp = (user.total_xp or 0) + xp
    # Simple leveling: level = 1 + total_xp // 100
    user.level = 1 + user.total_xp // 100
    db.flush()


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/lessons", response_model=list[LessonListItemV2])
def list_lessons_v2(current_user: CurrentUser, db: DB):
    """List all 23 lessons with unlock status for the current student."""
    # Fetch all progress rows for this student in one query
    all_progress = db.query(MedineV2Progress).filter_by(
        student_id=current_user.id,
    ).all()
    progress_map: dict[int, MedineV2Progress] = {p.lesson_number: p for p in all_progress}

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
def get_lesson_v2(lesson_number: int, current_user: CurrentUser):
    """Get full V2 content for a lesson."""
    lesson = _LESSONS.get(str(lesson_number))
    if not lesson:
        raise HTTPException(status_code=404, detail=f"Lesson {lesson_number} not found")
    return LessonContentV2(**lesson)


@router.post("/lessons/{lesson_number}/progress", response_model=LessonProgressV2)
def update_progress_v2(
    lesson_number: int,
    body: ProgressUpdateV2,
    current_user: CurrentUser,
    db: DB,
):
    """Update progress for a lesson step (persisted to DB)."""
    if str(lesson_number) not in _LESSONS:
        raise HTTPException(status_code=404, detail=f"Lesson {lesson_number} not found")

    progress = _get_or_create_progress(db, current_user.id, lesson_number)

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
            progress.stars = max(progress.stars, 3)
        elif progress.quiz_score >= 60:
            progress.stars = max(progress.stars, 2)
        else:
            progress.stars = max(progress.stars, 1)
        progress.is_completed = True

    progress.updated_at = datetime.now(timezone.utc)
    db.commit()
    return _progress_to_schema(progress)


@router.post("/lessons/{lesson_number}/quiz/submit", response_model=QuizResultV2)
def submit_quiz_v2(
    lesson_number: int,
    body: QuizSubmitV2,
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

        # Find question — handle both str and int IDs
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

    # Stars — minimum 40% to pass (1 star), otherwise 0 stars (fail)
    if score >= 85:
        stars = 3
    elif score >= 60:
        stars = 2
    elif score >= 40:
        stars = 1
    else:
        stars = 0

    # XP: base 5 per correct + speed bonus
    xp = correct_count * 5
    if body.time_ms > 0 and body.time_ms < total * 5000:
        xp += total * 2

    # Persist progress
    progress = _get_or_create_progress(db, current_user.id, lesson_number)
    progress.quiz_score = score
    progress.stars = max(progress.stars, stars)
    progress.is_completed = stars >= 1  # Only mark complete if passed
    progress.xp_earned = (progress.xp_earned or 0) + xp
    progress.updated_at = datetime.now(timezone.utc)

    # Update user's total XP
    _update_xp_on_user(db, current_user, xp)

    db.commit()

    return QuizResultV2(
        score=score,
        total=total,
        correct=correct_count,
        stars=stars,
        xp_earned=xp,
        results=results,
    )


# ── Flashcard endpoints ─────────────────────────────────────────────────────

@router.get("/flashcards", response_model=list[dict])
def get_flashcards_for_review(current_user: CurrentUser, db: DB):
    """
    Return all flashcards from completed lessons for review.
    Groups flashcards by lesson with metadata.
    """
    # Get all completed lessons for this student
    completed = db.query(MedineV2Progress).filter_by(
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
                "part_number": lesson["part_number"],
                "cards": cards,
            })

    return all_flashcards


@router.get("/stats", response_model=dict)
def get_student_stats(current_user: CurrentUser, db: DB):
    """Return aggregated student stats for the Médine V2 module."""
    all_progress = db.query(MedineV2Progress).filter_by(
        student_id=current_user.id,
    ).all()

    total_lessons = len(_LESSONS)
    completed = [p for p in all_progress if p.is_completed]
    total_stars = sum(p.stars for p in all_progress)
    total_xp = sum(p.xp_earned for p in all_progress)
    max_stars = total_lessons * 3

    return {
        "total_lessons": total_lessons,
        "completed_lessons": len(completed),
        "completion_pct": round(len(completed) / total_lessons * 100, 1) if total_lessons > 0 else 0,
        "total_stars": total_stars,
        "max_stars": max_stars,
        "total_xp": total_xp,
        "current_level": current_user.level or 1,
    }


# ── Boss Quiz endpoints ────────────────────────────────────────────────────

@router.get("/parts/{part_number}/quiz", response_model=BossQuizContent)
def get_boss_quiz(part_number: int, current_user: CurrentUser):
    """Get the boss quiz for a specific part."""
    quiz_data = _BOSS_QUIZZES.get(str(part_number))
    if not quiz_data:
        raise HTTPException(status_code=404, detail=f"No boss quiz for part {part_number}")
    return BossQuizContent(**quiz_data)


@router.post("/parts/{part_number}/quiz/submit", response_model=BossQuizResult)
def submit_boss_quiz(
    part_number: int,
    body: QuizSubmitV2,
    current_user: CurrentUser,
    db: DB,
):
    """Submit boss quiz answers and return scored result."""
    quiz_data = _BOSS_QUIZZES.get(str(part_number))
    if not quiz_data:
        raise HTTPException(status_code=404, detail=f"No boss quiz for part {part_number}")

    questions = quiz_data.get("questions", [])
    total = len(questions)
    if total == 0:
        raise HTTPException(status_code=400, detail="No questions in this boss quiz")

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
    passed = score >= quiz_data.get("passing_score", 70)

    if score >= 85:
        stars = 3
    elif score >= 60:
        stars = 2
    else:
        stars = 1

    # XP: 8 per correct for boss quiz (higher than regular)
    xp = correct_count * 8
    if passed:
        xp += 20  # Bonus for passing

    # Mark all lessons in this part as having the boss quiz passed
    # by updating XP on user
    _update_xp_on_user(db, current_user, xp)
    db.commit()

    return BossQuizResult(
        score=score,
        total=total,
        correct=correct_count,
        stars=stars,
        xp_earned=xp,
        passed=passed,
        results=results,
    )


# ── Final Exam endpoints ───────────────────────────────────────────────────

@router.get("/exam", response_model=FinalExamContent)
def get_final_exam(current_user: CurrentUser):
    """Get the final comprehensive exam."""
    if not _FINAL_EXAM or not _FINAL_EXAM.get("questions"):
        raise HTTPException(status_code=404, detail="Final exam not available")
    return FinalExamContent(**_FINAL_EXAM)


@router.post("/exam/submit", response_model=FinalExamResult)
def submit_final_exam(
    body: QuizSubmitV2,
    current_user: CurrentUser,
    db: DB,
):
    """Submit final exam answers and return scored result."""
    if not _FINAL_EXAM or not _FINAL_EXAM.get("questions"):
        raise HTTPException(status_code=404, detail="Final exam not available")

    questions = _FINAL_EXAM["questions"]
    total = len(questions)

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
    passed = score >= _FINAL_EXAM.get("passing_score", 70)

    if score >= 85:
        stars = 3
    elif score >= 60:
        stars = 2
    else:
        stars = 1

    # XP: 10 per correct for final exam (highest value)
    xp = correct_count * 10
    if passed:
        xp += 50  # Big bonus for passing final

    _update_xp_on_user(db, current_user, xp)
    db.commit()

    return FinalExamResult(
        score=score,
        total=total,
        correct=correct_count,
        stars=stars,
        xp_earned=xp,
        passed=passed,
        results=results,
    )


# ── Diagnostic CAT endpoints ──────────────────────────────────────────────

@router.get("/diagnostic", response_model=DiagnosticContent)
def get_diagnostic(current_user: CurrentUser):
    """Get the adaptive diagnostic placement test."""
    if not _DIAGNOSTIC or not _DIAGNOSTIC.get("questions"):
        raise HTTPException(status_code=404, detail="Diagnostic test not available")
    return DiagnosticContent(
        test_name=_DIAGNOSTIC["test_name"],
        total_questions=_DIAGNOSTIC["total_questions"],
        estimated_time=_DIAGNOSTIC["estimated_time"],
        questions=_DIAGNOSTIC["questions"],
    )


@router.post("/diagnostic/submit", response_model=DiagnosticResult)
def submit_diagnostic(
    body: DiagnosticSubmit,
    current_user: CurrentUser,
    db: DB,
):
    """Submit diagnostic answers and return placement result with competency radar."""
    if not _DIAGNOSTIC or not _DIAGNOSTIC.get("questions"):
        raise HTTPException(status_code=404, detail="Diagnostic test not available")

    questions = _DIAGNOSTIC["questions"]
    total = len(questions)

    correct_count = 0
    results = []
    correct_ids = set()

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
                correct_ids.add(q_id)
            results.append({
                "question_id": q_id,
                "selected": selected,
                "correct": question["correct"],
                "is_correct": is_correct,
                "explanation": question.get("explanation"),
                "adaptive_hint": question.get("adaptive_hint"),
                "skill_tested": question.get("skill_tested"),
            })

    # Determine level based on score
    score = (correct_count / total * 100) if total > 0 else 0
    logic = _DIAGNOSTIC.get("diagnostic_logic", {})

    # Find the right level bracket
    level_info = logic.get("0-2", {})  # default
    if correct_count >= 9:
        level_info = logic.get("9-10", level_info)
    elif correct_count >= 7:
        level_info = logic.get("7-8", level_info)
    elif correct_count >= 5:
        level_info = logic.get("5-6", level_info)
    elif correct_count >= 3:
        level_info = logic.get("3-4", level_info)

    # Calculate competency scores for radar chart
    competencies_def = _DIAGNOSTIC.get("competencies", [])
    competency_scores = []
    for comp in competencies_def:
        comp_questions = comp.get("questions", [])
        if comp_questions:
            comp_correct = sum(1 for qid in comp_questions if qid in correct_ids)
            comp_score = comp_correct / len(comp_questions)
        else:
            comp_score = 0.0
        competency_scores.append(CompetencyScore(
            id=comp["id"],
            name=comp["name"],
            score=comp_score,
        ))

    # Unlock all lessons up to start_at_lesson by creating progress rows
    start_at = level_info.get("start_at", 1)
    if start_at > 1:
        for ln in range(1, start_at):
            existing = db.query(MedineV2Progress).filter_by(
                student_id=current_user.id,
                lesson_number=ln,
            ).first()
            if not existing:
                db.add(MedineV2Progress(
                    student_id=current_user.id,
                    lesson_number=ln,
                    stars=1,
                    is_completed=True,
                    current_step="diagnostic_skip",
                ))
        db.commit()

    return DiagnosticResult(
        score=score,
        total=total,
        correct=correct_count,
        level=level_info.get("level", "Débutant"),
        start_at_lesson=start_at,
        start_at_part=level_info.get("start_part", 1),
        message=level_info.get("message", ""),
        competencies=competency_scores,
        results=results,
    )
