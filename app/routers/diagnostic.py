"""
Diagnostic Router — CAT-based adaptive testing API endpoints.

CAT Logic:
- Start with Pool A (difficulty=1)
- If first 2 correct → skip rest of pool, advance to next
- If 0/2 correct → STOP, recommend Partie 1
- If 1/2 → complete remaining pool, then advance
- Max 12 questions, min 4
"""
import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models.diagnostic import DiagnosticQuestion, DiagnosticSession, DiagnosticResult
from ..models.user import User
from ..core.dependencies import get_current_user


# ==================== Pydantic Schemas ====================

class DiagnosticQuestionResponse(BaseModel):
    id: uuid.UUID
    question: str
    options: list[str]
    difficulty: int
    skill_tested: str

    class Config:
        from_attributes = True


class StartDiagnosticResponse(BaseModel):
    session_id: uuid.UUID
    first_question: DiagnosticQuestionResponse


class AnswerRequest(BaseModel):
    question_id: uuid.UUID
    selected: int  # index of selected option


class AnswerResponse(BaseModel):
    is_correct: bool
    explanation: str | None = None
    next_question: DiagnosticQuestionResponse | None = None
    is_finished: bool = False


class DiagnosticResultResponse(BaseModel):
    score: int
    level: str
    level_message: str
    skill_scores: dict
    recommended_path: list[dict]
    estimated_duration: str


# ==================== Router Setup ====================

router = APIRouter(prefix="/api/diagnostic", tags=["diagnostic"])


# ==================== Helper Functions ====================

def _get_questions_by_pool(db: Session, pool: str) -> list[DiagnosticQuestion]:
    """Get all questions for a given pool, sorted by sort_order."""
    difficulty_map = {"A": 1, "B": 2, "C": 3}
    difficulty = difficulty_map.get(pool, 1)

    questions = (
        db.query(DiagnosticQuestion)
        .filter(
            DiagnosticQuestion.pool == pool,
            DiagnosticQuestion.difficulty == difficulty,
        )
        .order_by(DiagnosticQuestion.sort_order)
        .all()
    )
    return questions


def _get_next_question(
    db: Session,
    session: DiagnosticSession,
) -> DiagnosticQuestion | None:
    """
    Implement CAT logic to determine next question.

    Returns:
        Next question or None if test is finished.
    """
    answers = session.answers or []
    current_pool = session.current_pool

    # Max 12 questions, min 4
    if len(answers) >= 12:
        return None

    # Determine if we should ask questions from the current pool
    pool_questions = _get_questions_by_pool(db, current_pool)

    if not pool_questions:
        # No more questions in this pool, move to next
        if current_pool == "A":
            session.current_pool = "B"
            session.current_pool_index = 0
            return _get_next_question(db, session)
        elif current_pool == "B":
            session.current_pool = "C"
            session.current_pool_index = 0
            return _get_next_question(db, session)
        else:
            # All pools exhausted
            return None

    # Get answers for this pool so far
    pool_answer_count = sum(
        1 for ans in answers
        if ans.get("pool") == current_pool
    )

    # First 2 questions of the pool
    if pool_answer_count < 2:
        # Ask next question from the first 2
        return pool_questions[pool_answer_count]

    # Check performance on first 2 questions
    first_two_answers = [ans for ans in answers if ans.get("pool") == current_pool][:2]
    correct_count = sum(1 for ans in first_two_answers if ans.get("is_correct"))

    if correct_count == 2:
        # All correct: skip rest of pool, move to next
        if current_pool == "A":
            session.current_pool = "B"
        elif current_pool == "B":
            session.current_pool = "C"
        else:
            return None  # No next pool
        session.current_pool_index = 0
        return _get_next_question(db, session)

    elif correct_count == 0:
        # None correct: stop the test
        return None

    else:
        # 1 correct: ask remaining questions from this pool
        remaining_questions = pool_answer_count
        if remaining_questions < len(pool_questions):
            return pool_questions[remaining_questions]
        else:
            # All remaining questions asked, move to next pool
            if current_pool == "A":
                session.current_pool = "B"
            elif current_pool == "B":
                session.current_pool = "C"
            else:
                return None
            session.current_pool_index = 0
            return _get_next_question(db, session)


def _calculate_diagnostic_level(score: int) -> tuple[str, str]:
    """
    Calculate level based on score (0-10).

    Returns:
        (level_name, level_message)
    """
    levels = {
        (0, 2): (
            "explorateur",
            "Tu débutes une aventure incroyable...",
        ),
        (3, 4): (
            "voyageur",
            "Tu as déjà les bases...",
        ),
        (5, 6): (
            "chercheur",
            "Tes fondations sont solides...",
        ),
        (7, 8): (
            "savant",
            "Impressionnant...",
        ),
        (9, 10): (
            "gardien",
            "Tu maîtrises le Tome 1...",
        ),
    }

    for (min_score, max_score), (level_name, message) in levels.items():
        if min_score <= score <= max_score:
            return level_name, message

    # Default fallback
    return "explorateur", "Tu débutes une aventure incroyable..."


def _calculate_skill_scores(
    db: Session,
    session: DiagnosticSession,
) -> dict[str, float]:
    """
    Calculate skill scores from session answers.

    Returns:
        dict mapping skill_tested -> percentage (0-100)
    """
    answers = session.answers or []
    if not answers:
        return {}

    skill_stats: dict[str, dict] = {}

    for answer in answers:
        question_id = answer.get("question_id")
        is_correct = answer.get("is_correct")

        question = db.query(DiagnosticQuestion).filter(
            DiagnosticQuestion.id == uuid.UUID(question_id)
        ).first()

        if not question:
            continue

        skill = question.skill_tested
        if skill not in skill_stats:
            skill_stats[skill] = {"correct": 0, "total": 0}

        skill_stats[skill]["total"] += 1
        if is_correct:
            skill_stats[skill]["correct"] += 1

    # Convert to percentages
    skill_scores = {}
    for skill, stats in skill_stats.items():
        percentage = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
        skill_scores[skill] = round(percentage, 1)

    return skill_scores


def _build_recommended_path(
    db: Session,
    skill_scores: dict,
    score: int,
) -> list[dict]:
    """
    Build recommended learning path based on skill scores and overall score.

    Returns:
        list of {"lesson": str, "status": "mastered"|"to_do"}
    """
    # Simple heuristic: if skill score > 70%, mark as mastered
    path = []
    for skill, percentage in skill_scores.items():
        status = "mastered" if percentage > 70 else "to_do"
        path.append({
            "skill": skill,
            "score": percentage,
            "status": status,
        })

    # Sort by score descending
    path.sort(key=lambda x: x["score"], reverse=True)

    return path


def _estimate_duration(score: int) -> str:
    """Estimate duration based on score."""
    if score <= 2:
        return "4-6 semaines"
    elif score <= 4:
        return "3-4 semaines"
    elif score <= 6:
        return "2-3 semaines"
    elif score <= 8:
        return "1-2 semaines"
    else:
        return "Révision rapide"


# ==================== Endpoints ====================

@router.post("/start", response_model=StartDiagnosticResponse)
def start_diagnostic(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Start a new diagnostic session.
    - Create DiagnosticSession for the student
    - Get first question from Pool A
    - Return StartDiagnosticResponse
    """
    # Create session
    session = DiagnosticSession(
        student_id=current_user.id,
        current_pool="A",
        current_pool_index=0,
        answers=[],
    )
    db.add(session)
    db.flush()

    # Get first question from Pool A
    first_question = _get_next_question(db, session)
    if not first_question:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Pas de questions disponibles pour le diagnostic",
        )

    db.commit()

    question_response = DiagnosticQuestionResponse(
        id=first_question.id,
        question=first_question.question,
        options=first_question.options,
        difficulty=first_question.difficulty,
        skill_tested=first_question.skill_tested,
    )

    return StartDiagnosticResponse(
        session_id=session.id,
        first_question=question_response,
    )


@router.post("/{session_id}/answer", response_model=AnswerResponse)
def answer_diagnostic_question(
    session_id: uuid.UUID,
    request: AnswerRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Submit an answer to a diagnostic question.
    Implements CAT logic and returns next question or result.
    """
    # Validate session
    session = db.query(DiagnosticSession).filter(
        DiagnosticSession.id == session_id,
        DiagnosticSession.student_id == current_user.id,
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session de diagnostic non trouvée",
        )

    if session.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette session est déjà terminée",
        )

    # Get the question
    question = db.query(DiagnosticQuestion).filter(
        DiagnosticQuestion.id == request.question_id,
    ).first()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question non trouvée",
        )

    # Validate answer index
    if not (0 <= request.selected < len(question.options)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Index de réponse invalide",
        )

    # Check if answer is correct
    is_correct = request.selected == question.correct

    # Record answer
    if session.answers is None:
        session.answers = []

    session.answers.append({
        "question_id": str(request.question_id),
        "pool": question.pool,
        "difficulty": question.difficulty,
        "skill_tested": question.skill_tested,
        "selected": request.selected,
        "correct": question.correct,
        "is_correct": is_correct,
    })

    # Get next question
    next_question = _get_next_question(db, session)

    explanation = None
    if question.explanation:
        explanation = question.explanation

    response_data = {
        "is_correct": is_correct,
        "explanation": explanation,
        "next_question": None,
        "is_finished": False,
    }

    if next_question:
        question_response = DiagnosticQuestionResponse(
            id=next_question.id,
            question=next_question.question,
            options=next_question.options,
            difficulty=next_question.difficulty,
            skill_tested=next_question.skill_tested,
        )
        response_data["next_question"] = question_response
    else:
        # Test is finished
        response_data["is_finished"] = True
        session.is_completed = True
        session.completed_at = datetime.utcnow()

    db.commit()

    return AnswerResponse(**response_data)


@router.get("/{session_id}/result", response_model=DiagnosticResultResponse)
def get_diagnostic_result(
    session_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get diagnostic result for a completed session.
    - Calculate level based on score
    - Calculate skill scores from answers
    - Build recommended path
    - Estimate duration
    - Save DiagnosticResult if not already saved
    - Mark user.diagnostic_completed = True
    """
    # Validate session
    session = db.query(DiagnosticSession).filter(
        DiagnosticSession.id == session_id,
        DiagnosticSession.student_id == current_user.id,
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session de diagnostic non trouvée",
        )

    if not session.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La session n'est pas encore terminée",
        )

    # Check if result already exists
    result = db.query(DiagnosticResult).filter(
        DiagnosticResult.session_id == session_id,
    ).first()

    if result:
        return DiagnosticResultResponse(
            score=result.score,
            level=result.level,
            level_message=result.level_message,
            skill_scores=result.skill_scores or {},
            recommended_path=result.recommended_path or [],
            estimated_duration=result.estimated_duration or "",
        )

    # Calculate score (number of correct answers)
    answers = session.answers or []
    score = sum(1 for ans in answers if ans.get("is_correct"))

    # Calculate level
    level, level_message = _calculate_diagnostic_level(score)

    # Calculate skill scores
    skill_scores = _calculate_skill_scores(db, session)

    # Build recommended path
    recommended_path = _build_recommended_path(db, skill_scores, score)

    # Estimate duration
    estimated_duration = _estimate_duration(score)

    # Save result
    result = DiagnosticResult(
        session_id=session_id,
        student_id=current_user.id,
        score=score,
        level=level,
        level_message=level_message,
        skill_scores=skill_scores,
        recommended_path=recommended_path,
        estimated_duration=estimated_duration,
    )
    db.add(result)

    # Mark diagnostic as completed for the user
    current_user.diagnostic_completed = True

    db.commit()

    return DiagnosticResultResponse(
        score=score,
        level=level,
        level_message=level_message,
        skill_scores=skill_scores,
        recommended_path=recommended_path,
        estimated_duration=estimated_duration,
    )
