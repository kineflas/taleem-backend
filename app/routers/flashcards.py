"""
Flashcard Router — SRS-based spaced repetition API endpoints.
"""
import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.flashcard import FlashcardCard, FlashcardProgress
from ..models.user import User
from ..core.dependencies import get_current_user
from ..services import srs_service, xp_service


# ==================== Pydantic Schemas ====================

class FlashcardCardResponse(BaseModel):
    id: uuid.UUID
    card_id_str: str
    lesson_number: int
    part_number: int
    front_ar: str
    back_fr: str
    category: str | None = None
    arabic_example: str | None = None
    french_example: str | None = None

    class Config:
        from_attributes = True


class FlashcardProgressResponse(BaseModel):
    card: FlashcardCardResponse
    ease_factor: float
    interval_days: int
    repetitions: int
    next_review: datetime
    last_quality: int | None = None
    review_count: int

    class Config:
        from_attributes = True


class ReviewRequest(BaseModel):
    quality: int  # 1, 3, 4, or 5


class ReviewResponse(BaseModel):
    card_id: uuid.UUID
    new_ease_factor: float
    new_interval_days: int
    next_review: datetime
    xp_earned: int


class SRSStatsResponse(BaseModel):
    total_started: int
    total_available: int
    due_today: int
    mastered: int
    learning: int


# ==================== Router Setup ====================

router = APIRouter(prefix="/api/flashcards", tags=["flashcards"])


# ==================== Endpoints ====================

@router.get("/due", response_model=list[FlashcardProgressResponse])
def get_due_flashcards(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get due flashcards (max 50) for the current student.
    Returns list of FlashcardProgressResponse with joined card data.
    """
    due_cards = srs_service.get_due_cards(db, current_user.id, limit=50)

    result = []
    for progress in due_cards:
        card = progress.card
        card_response = FlashcardCardResponse(
            id=card.id,
            card_id_str=card.card_id_str,
            lesson_number=card.lesson_number,
            part_number=card.part_number,
            front_ar=card.front_ar,
            back_fr=card.back_fr,
            category=card.category,
            arabic_example=card.arabic_example,
            french_example=card.french_example,
        )
        result.append(
            FlashcardProgressResponse(
                card=card_response,
                ease_factor=progress.ease_factor,
                interval_days=progress.interval_days,
                repetitions=progress.repetitions,
                next_review=progress.next_review,
                last_quality=progress.last_quality,
                review_count=progress.review_count,
            )
        )

    return result


@router.get("/new/{lesson_number}", response_model=list[FlashcardCardResponse])
def get_new_cards_for_lesson(
    lesson_number: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get new cards for a specific lesson (max 15 per day).
    Returns list of FlashcardCardResponse.
    """
    cards = srs_service.get_new_cards_for_lesson(db, current_user.id, lesson_number, limit=15)

    result = []
    for card in cards:
        result.append(
            FlashcardCardResponse(
                id=card.id,
                card_id_str=card.card_id_str,
                lesson_number=card.lesson_number,
                part_number=card.part_number,
                front_ar=card.front_ar,
                back_fr=card.back_fr,
                category=card.category,
                arabic_example=card.arabic_example,
                french_example=card.french_example,
            )
        )

    return result


@router.post("/{card_id}/review", response_model=ReviewResponse)
def review_flashcard(
    card_id: uuid.UUID,
    request: ReviewRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Review a flashcard.
    - Creates FlashcardProgress if doesn't exist
    - Applies SM-2 algorithm via srs_service.update_card_srs()
    - Awards 3 XP per review via xp_service.award_xp()
    - Returns ReviewResponse
    """
    # Validate quality value
    if request.quality not in [1, 3, 4, 5]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quality must be one of: 1, 3, 4, 5",
        )

    # Get or create progress record
    progress = db.query(FlashcardProgress).filter(
        FlashcardProgress.student_id == current_user.id,
        FlashcardProgress.card_id == card_id,
    ).first()

    if not progress:
        progress = srs_service.initialize_card_progress(db, current_user.id, card_id)

    # Apply SM-2 algorithm
    progress = srs_service.update_card_srs(progress, request.quality)
    db.commit()

    # Award XP (3 XP per review)
    xp_result = xp_service.award_xp(
        db,
        current_user.id,
        source="flashcard_review",
        xp_amount=3,
        source_id=str(card_id),
    )
    db.commit()

    return ReviewResponse(
        card_id=card_id,
        new_ease_factor=progress.ease_factor,
        new_interval_days=progress.interval_days,
        next_review=progress.next_review,
        xp_earned=xp_result.get("xp_earned", 0),
    )


@router.get("/stats", response_model=SRSStatsResponse)
def get_srs_stats(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get SRS statistics for the current student.
    Returns SRSStatsResponse via srs_service.get_srs_stats().
    """
    stats = srs_service.get_srs_stats(db, current_user.id)
    return SRSStatsResponse(**stats)
