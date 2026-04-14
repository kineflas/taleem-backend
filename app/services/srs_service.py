"""
SRS Service — SM-2 spaced repetition algorithm for flashcards.

Quality mapping:
  1 = "À revoir"  (reset)
  3 = "Difficile"  (no increase)
  4 = "Bien"       (normal increase)
  5 = "Facile"     (boosted increase)
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session as DBSession
from uuid import UUID

from ..models.flashcard import FlashcardCard, FlashcardProgress


def update_card_srs(progress: FlashcardProgress, quality: int) -> FlashcardProgress:
    """
    Apply SM-2 algorithm to update a flashcard's SRS parameters.

    Formula:
    - If quality < 3: reset repetitions to 0, interval to 1 day
    - If quality >= 3:
      - repetitions == 0 → interval = 1
      - repetitions == 1 → interval = 3
      - repetitions >= 2 → interval = old_interval * ease_factor
      - repetitions += 1

    ease_factor = max(1.3, ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))

    If quality == 5 (Facile): interval *= 1.3 (boost)
    """
    if quality < 3:
        progress.repetitions = 0
        progress.interval_days = 1
    else:
        if progress.repetitions == 0:
            progress.interval_days = 1
        elif progress.repetitions == 1:
            progress.interval_days = 3
        else:
            progress.interval_days = max(1, int(progress.interval_days * progress.ease_factor))
        progress.repetitions += 1

    # Update ease factor
    progress.ease_factor = max(1.3,
        progress.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    )
    # Cap ease factor at 3.0
    progress.ease_factor = min(3.0, progress.ease_factor)

    # Boost for "Facile"
    if quality == 5:
        progress.interval_days = max(1, int(progress.interval_days * 1.3))

    progress.next_review = datetime.utcnow() + timedelta(days=progress.interval_days)
    progress.last_quality = quality
    progress.review_count += 1
    progress.updated_at = datetime.utcnow()

    return progress


def get_due_cards(db: DBSession, student_id: UUID, limit: int = 50) -> list:
    """Get flashcards due for review, ordered by most overdue first."""
    now = datetime.utcnow()
    return (
        db.query(FlashcardProgress)
        .filter(
            FlashcardProgress.student_id == student_id,
            FlashcardProgress.next_review <= now,
        )
        .order_by(FlashcardProgress.next_review.asc())
        .limit(limit)
        .all()
    )


def get_new_cards_for_lesson(db: DBSession, student_id: UUID, lesson_number: int, limit: int = 15) -> list:
    """Get flashcard cards for a lesson that the student hasn't started yet."""
    # Find cards for the lesson that don't have progress records
    started_card_ids = (
        db.query(FlashcardProgress.card_id)
        .filter(FlashcardProgress.student_id == student_id)
        .subquery()
    )
    return (
        db.query(FlashcardCard)
        .filter(
            FlashcardCard.lesson_number == lesson_number,
            ~FlashcardCard.id.in_(started_card_ids),
        )
        .order_by(FlashcardCard.sort_order)
        .limit(limit)
        .all()
    )


def get_srs_stats(db: DBSession, student_id: UUID) -> dict:
    """Get SRS statistics for a student."""
    from sqlalchemy import func
    now = datetime.utcnow()

    total = db.query(func.count(FlashcardProgress.id)).filter(
        FlashcardProgress.student_id == student_id
    ).scalar() or 0

    due_today = db.query(func.count(FlashcardProgress.id)).filter(
        FlashcardProgress.student_id == student_id,
        FlashcardProgress.next_review <= now,
    ).scalar() or 0

    mastered = db.query(func.count(FlashcardProgress.id)).filter(
        FlashcardProgress.student_id == student_id,
        FlashcardProgress.interval_days > 21,
    ).scalar() or 0

    learning = total - mastered

    total_cards_available = db.query(func.count(FlashcardCard.id)).scalar() or 0

    return {
        "total_started": total,
        "total_available": total_cards_available,
        "due_today": due_today,
        "mastered": mastered,
        "learning": learning,
    }


def initialize_card_progress(db: DBSession, student_id: UUID, card_id: UUID) -> FlashcardProgress:
    """Create initial progress record for a new card."""
    progress = FlashcardProgress(
        student_id=student_id,
        card_id=card_id,
        ease_factor=2.5,
        interval_days=0,
        repetitions=0,
        next_review=datetime.utcnow(),
        review_count=0,
    )
    db.add(progress)
    db.flush()
    return progress
