"""
Lesson Detail API — serves structured lesson content from CurriculumItems.
Endpoints for listing lessons, fetching lesson details, tracking progress, and submitting quizzes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timezone
import json

from ..database import get_db
from ..core.dependencies import CurrentUser, get_current_user
from ..models.user import User
from typing import Optional
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

_optional_bearer = HTTPBearer(auto_error=False)


def _get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_optional_bearer),
    db: Session = Depends(get_db),
) -> User | None:
    """Optional auth — returns User if valid token, None otherwise."""
    if credentials is None:
        return None
    try:
        from ..core.security import decode_token
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
        import uuid as _uuid
        return db.query(User).filter(User.id == _uuid.UUID(user_id), User.is_active == True).first()
    except Exception:
        return None
from ..models.curriculum import (
    CurriculumProgram, CurriculumUnit, CurriculumItem,
    StudentEnrollment, StudentItemProgress,
    CurriculumType, UnitType, EnrollmentMode,
)
from ..schemas.lesson import (
    LessonDetailResponse, LessonListItem, LessonTheory,
    TheorySection, ExampleItem, VocabItem, IllustrationItem,
    QuizQuestion, LessonProgress, LessonProgressUpdate,
    QuizSubmission, QuizResultResponse,
    DialogueLine, DialogueContent,
)

router = APIRouter(prefix="/api/lessons", tags=["Lessons"])

# Part number mapping for the 23 Medine lessons
LESSON_TO_PART = {
    1: 1, 2: 1, 3: 1, 4: 1,      # Part 1
    5: 2, 6: 2, 7: 2, 8: 2,      # Part 2
    9: 3, 10: 3, 11: 3,          # Part 3
    12: 4, 13: 4, 14: 4, 15: 4,  # Part 4
    16: 5, 17: 5, 18: 5,         # Part 5
    19: 6, 20: 6, 21: 6,         # Part 6
    22: 7, 23: 7,                # Part 7
}


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════


def _get_or_create_enrollment(db: Session, student_id: UUID) -> StudentEnrollment:
    """Get or create a student enrollment in the MEDINE_T1 program."""
    program = db.query(CurriculumProgram).filter_by(
        curriculum_type=CurriculumType.MEDINE_T1
    ).first()
    if not program:
        raise HTTPException(status_code=404, detail="Programme Medine non trouvé")

    enrollment = db.query(StudentEnrollment).filter_by(
        student_id=student_id,
        curriculum_program_id=program.id,
    ).first()
    if not enrollment:
        enrollment = StudentEnrollment(
            student_id=student_id,
            curriculum_program_id=program.id,
            mode=EnrollmentMode.STUDENT_AUTONOMOUS,
        )
        db.add(enrollment)
        db.flush()
    return enrollment


def _get_lesson_item(db: Session, lesson_number: int):
    """Get the CurriculumItem for a lesson by number.

    Returns: (program, unit, item)
    """
    program = db.query(CurriculumProgram).filter_by(
        curriculum_type=CurriculumType.MEDINE_T1
    ).first()
    if not program:
        raise HTTPException(status_code=404, detail="Programme Medine non trouvé")

    unit = db.query(CurriculumUnit).filter_by(
        curriculum_program_id=program.id,
        number=lesson_number,
    ).first()
    if not unit:
        raise HTTPException(status_code=404, detail=f"Leçon {lesson_number} non trouvée")

    item = db.query(CurriculumItem).filter_by(
        curriculum_unit_id=unit.id,
        number=1,
    ).first()

    return program, unit, item


def _extract_theory(extra_data: dict | None) -> LessonTheory:
    """Extract theory content from item's extra_data."""
    if not extra_data:
        return LessonTheory()

    sections = []
    for sec in extra_data.get("explanation_sections", []):
        sections.append(TheorySection(
            title_fr=sec.get("title_fr", ""),
            content_fr=sec.get("content_fr", ""),
            content_ar=sec.get("content_ar"),
            tip_fr=sec.get("tip_fr"),
        ))

    examples = []
    for ex in extra_data.get("examples", []):
        examples.append(ExampleItem(
            arabic=ex.get("arabic", ""),
            transliteration=ex.get("transliteration"),
            translation_fr=ex.get("translation_fr", ""),
            breakdown_fr=ex.get("breakdown_fr"),
            grammatical_note_fr=ex.get("grammatical_note_fr"),
        ))

    vocab = []
    for (arabic, translation_fr, transliteration) in extra_data.get("vocab", []):
        vocab.append(VocabItem(
            arabic=arabic,
            translation_fr=translation_fr,
            transliteration=transliteration,
        ))

    illustrations = []
    for illus in extra_data.get("illustrations", []):
        illustrations.append(IllustrationItem(
            type=illus.get("type", ""),
            title_fr=illus.get("title_fr", ""),
            data=illus.get("data"),
        ))

    # Parse dialogue content if present
    dialogue_data = extra_data.get("dialogue")
    dialogue = None
    if dialogue_data and isinstance(dialogue_data, dict):
        dialogue_lines = [
            DialogueLine(
                speaker_ar=line.get("speaker_ar", ""),
                arabic=line.get("arabic", ""),
                french=line.get("french", ""),
            )
            for line in dialogue_data.get("lines", [])
        ]
        dialogue = DialogueContent(
            situation=dialogue_data.get("situation"),
            lines=dialogue_lines,
        )

    # Parse examples from MD (examples_md field)
    examples_md = extra_data.get("examples_md", [])
    for ex in examples_md:
        examples.append(ExampleItem(
            arabic=ex.get("arabic", ""),
            translation_fr=ex.get("translation_fr", ""),
            grammatical_note_fr=ex.get("grammatical_note_fr"),
        ))

    return LessonTheory(
        sections=sections,
        examples=examples,
        vocab=vocab,
        illustrations=illustrations,
        grammar_summary=extra_data.get("grammar"),
        objective=extra_data.get("objective"),
        coin_experts=extra_data.get("coin_experts"),
        dialogue=dialogue,
        mise_en_situation=extra_data.get("mise_en_situation"),
        exercises_md=extra_data.get("exercises_md"),
        pronunciation=extra_data.get("pronunciation"),
    )


def _extract_quiz_questions(extra_data: dict | None, key: str) -> list[QuizQuestion]:
    """Extract quiz questions from extra_data[key]."""
    if not extra_data or key not in extra_data:
        return []

    questions = []
    for q in extra_data[key]:
        questions.append(QuizQuestion(
            id=q.get("id", ""),
            question=q.get("question", ""),
            options=q.get("options", []),
            correct=q.get("correct", 0),
            explanation=q.get("explanation"),
        ))
    return questions


def _get_previous_lesson_stars(
    db: Session, enrollment: StudentEnrollment, lesson_number: int
) -> int:
    """Get the stars earned on the previous lesson, or 0 if no previous lesson."""
    if lesson_number <= 1:
        return 0

    prev_program, prev_unit, prev_item = _get_lesson_item(db, lesson_number - 1)
    if not prev_item:
        return 0

    progress = db.query(StudentItemProgress).filter_by(
        enrollment_id=enrollment.id,
        curriculum_item_id=prev_item.id,
    ).first()

    if not progress:
        return 0

    # mastery_level is 1, 2, or 3, which we interpret as stars
    return progress.mastery_level or 0


def _is_lesson_unlocked(
    db: Session, enrollment: StudentEnrollment, lesson_number: int
) -> bool:
    """Check if a lesson is unlocked.

    Rule: lesson N is unlocked if lesson N-1 has at least 1 star (or N==1)
    """
    if lesson_number <= 1:
        return True

    return _get_previous_lesson_stars(db, enrollment, lesson_number) >= 1


# ══════════════════════════════════════════════════════════════════════════════
# Routes
# ══════════════════════════════════════════════════════════════════════════════


@router.get("", response_model=list[LessonListItem])
def list_lessons(db: Session = Depends(get_db)):
    """
    Returns a list of all 23 Medine lessons with unlock status.
    Public endpoint (no auth required).
    """
    program = db.query(CurriculumProgram).filter_by(
        curriculum_type=CurriculumType.MEDINE_T1
    ).first()
    if not program:
        raise HTTPException(status_code=404, detail="Programme Medine non trouvé")

    units = db.query(CurriculumUnit).filter_by(
        curriculum_program_id=program.id
    ).order_by(CurriculumUnit.sort_order).all()

    results = []
    for unit in units:
        item = db.query(CurriculumItem).filter_by(
            curriculum_unit_id=unit.id,
            number=1,
        ).first()

        # No auth — so all lessons appear unlocked and no progress
        results.append(LessonListItem(
            unit_id=unit.id,
            lesson_number=unit.number,
            title_ar=unit.title_ar,
            title_fr=unit.title_fr or "",
            stars=0,
            is_completed=False,
            is_unlocked=True,
            is_mastered_by_diagnostic=False,
        ))

    return results


@router.get("/{lesson_number}", response_model=LessonDetailResponse)
def get_lesson_detail(
    lesson_number: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(_get_optional_user),
):
    """
    Returns full lesson detail including theory, quiz questions, and progress.
    Public endpoint, but shows progress if authenticated.
    """
    program, unit, item = _get_lesson_item(db, lesson_number)

    if not item:
        raise HTTPException(status_code=404, detail=f"Contenu de la leçon {lesson_number} non trouvé")

    extra_data = item.extra_data or {}

    # Determine unlock status and progress
    is_unlocked = True
    previous_lesson_stars = 0
    progress = None

    if current_user:
        # Authenticated: fetch or create enrollment and check progress
        enrollment = _get_or_create_enrollment(db, current_user.id)
        is_unlocked = _is_lesson_unlocked(db, enrollment, lesson_number)
        previous_lesson_stars = _get_previous_lesson_stars(db, enrollment, lesson_number)

        # Get progress
        progress_record = db.query(StudentItemProgress).filter_by(
            enrollment_id=enrollment.id,
            curriculum_item_id=item.id,
        ).first()

        if progress_record:
            progress = LessonProgress(
                theory_completed=progress_record.mastery_level is not None and progress_record.mastery_level >= 1,
                dialogue_completed=progress_record.mastery_level is not None and progress_record.mastery_level >= 2,
                exercises_score=None,  # Not tracked in StudentItemProgress
                quiz_score=None,  # Not tracked in StudentItemProgress
                stars=progress_record.mastery_level or 0,
                is_completed=progress_record.is_completed,
            )

    # Extract content
    theory = _extract_theory(extra_data)
    quiz_questions = _extract_quiz_questions(extra_data, "quiz")
    quiz_md_questions = _extract_quiz_questions(extra_data, "quiz_md")

    return LessonDetailResponse(
        unit_id=unit.id,
        lesson_number=lesson_number,
        part_number=LESSON_TO_PART.get(lesson_number, 1),
        title_ar=unit.title_ar,
        title_fr=unit.title_fr or "",
        description_fr=unit.description_fr,
        theory=theory,
        quiz_questions=quiz_questions,
        quiz_md_questions=quiz_md_questions,
        is_unlocked=is_unlocked,
        previous_lesson_stars=previous_lesson_stars,
        progress=progress,
    )


@router.post("/{lesson_number}/progress", response_model=dict)
def update_lesson_progress(
    lesson_number: int,
    body: LessonProgressUpdate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """
    Update lesson progress for a specific segment.
    Requires authentication.
    """
    program, unit, item = _get_lesson_item(db, lesson_number)

    if not item:
        raise HTTPException(status_code=404, detail=f"Leçon {lesson_number} non trouvée")

    # Get or create enrollment
    enrollment = _get_or_create_enrollment(db, current_user.id)

    # Get or create progress record
    progress = db.query(StudentItemProgress).filter_by(
        enrollment_id=enrollment.id,
        curriculum_item_id=item.id,
    ).first()

    if not progress:
        progress = StudentItemProgress(
            enrollment_id=enrollment.id,
            student_id=current_user.id,
            curriculum_item_id=item.id,
        )
        db.add(progress)

    # Update based on segment
    # Interpret body.value (0.0-1.0) as completion level
    # For simplicity: if value > 0, increment mastery_level on first completion
    if body.value > 0 and progress.mastery_level is None:
        progress.mastery_level = 1  # "seen"
    elif body.value >= 0.5 and progress.mastery_level and progress.mastery_level < 2:
        progress.mastery_level = 2  # "practiced"
    elif body.value >= 1.0 and progress.mastery_level and progress.mastery_level < 3:
        progress.mastery_level = 3  # "mastered"

    progress.last_attempt_at = datetime.now(timezone.utc)
    progress.attempt_count += 1

    db.commit()

    return {
        "message": "Progress updated",
        "segment": body.segment,
        "value": body.value,
        "mastery_level": progress.mastery_level,
    }


@router.post("/{lesson_number}/quiz/submit", response_model=QuizResultResponse)
def submit_quiz(
    lesson_number: int,
    body: QuizSubmission,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """
    Submit quiz answers and get scored results.
    Requires authentication.
    """
    program, unit, item = _get_lesson_item(db, lesson_number)

    if not item:
        raise HTTPException(status_code=404, detail=f"Leçon {lesson_number} non trouvée")

    extra_data = item.extra_data or {}

    # Get or create enrollment
    enrollment = _get_or_create_enrollment(db, current_user.id)

    # Get or create progress record
    progress = db.query(StudentItemProgress).filter_by(
        enrollment_id=enrollment.id,
        curriculum_item_id=item.id,
    ).first()

    if not progress:
        progress = StudentItemProgress(
            enrollment_id=enrollment.id,
            student_id=current_user.id,
            curriculum_item_id=item.id,
        )
        db.add(progress)

    # Combine quiz and quiz_md questions
    all_questions = {}
    for q in extra_data.get("quiz", []):
        all_questions[q["id"]] = q
    for q in extra_data.get("quiz_md", []):
        all_questions[q["id"]] = q

    # Score the answers
    correct_count = 0
    total_count = len(body.answers)
    results = []

    for answer in body.answers:
        question_id = answer.get("question_id")
        selected = answer.get("selected")

        if question_id not in all_questions:
            continue

        q = all_questions[question_id]
        correct_answer = q.get("correct", -1)
        is_correct = selected == correct_answer

        if is_correct:
            correct_count += 1

        results.append({
            "question_id": question_id,
            "selected": selected,
            "correct": correct_answer,
            "is_correct": is_correct,
        })

    # Calculate score
    score = (correct_count / total_count * 100) if total_count > 0 else 0.0

    # Calculate stars: <60% = 1★, <85% = 2★, ≥85% = 3★
    if score >= 85:
        stars = 3
    elif score >= 60:
        stars = 2
    else:
        stars = 1

    # Calculate XP: base 5 per question, +2 bonus if <5s per question
    xp_base = total_count * 5
    # Bonus if answers were quick (time_ms / num_questions < 5000 ms per q)
    avg_time_per_q = body.time_ms / total_count if total_count > 0 else float('inf')
    xp_bonus = 0
    if avg_time_per_q < 5000:
        xp_bonus = total_count * 2

    xp_earned = xp_base + xp_bonus

    # Update progress: set mastery_level to stars if this is better than before
    if progress.mastery_level is None or stars > progress.mastery_level:
        progress.mastery_level = stars

    progress.is_completed = True
    progress.completed_at = datetime.now(timezone.utc)
    progress.last_attempt_at = datetime.now(timezone.utc)
    progress.attempt_count += 1

    db.commit()

    return QuizResultResponse(
        score=score,
        total=total_count,
        correct=correct_count,
        stars=stars,
        xp_earned=int(xp_earned),
        results=results,
    )
