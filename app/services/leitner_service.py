"""
Leitner Box spaced repetition service for Taleem Quran learning.

The Leitner system uses 5 boxes with increasing review intervals:
  Box 1: review every 1 day (new / failed)
  Box 2: review every 2 days
  Box 3: review every 4 days
  Box 4: review every 8 days
  Box 5: review every 16 days (mastered)

Correct response → move card up one box (max 5)
Wrong response → move card back to Box 1, reset next_review_date to today
"""
import uuid
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from ..models.autonomous_learning import LeitnerCard, QuranWord, StudentModuleProgress


# Box intervals in days
BOX_INTERVALS = {
    1: 1,
    2: 2,
    3: 4,
    4: 8,
    5: 16,
}


def initialize_cards_for_student(
    db: Session, student_id: uuid.UUID, module: int
) -> list[LeitnerCard]:
    """
    Creates LeitnerCard entries for all QuranWords matching the given module.
    All cards start in Box 1 with next_review_date = today.

    Idempotent: skips words that already have a card for this student.

    Args:
        db: Database session
        student_id: UUID of the student
        module: Module number (1-5)

    Returns:
        List of created LeitnerCard objects
    """
    today = date.today()
    created_cards = []

    # Get all words for this module
    words = db.query(QuranWord).filter(QuranWord.module == module).all()

    for word in words:
        # Check if card already exists for this student-word pair
        existing_card = db.query(LeitnerCard).filter(
            LeitnerCard.student_id == student_id,
            LeitnerCard.word_id == word.id,
        ).first()

        if existing_card:
            continue

        # Create new card
        card = LeitnerCard(
            student_id=student_id,
            word_id=word.id,
            box=1,
            next_review_date=today,
            last_reviewed_at=None,
            total_reviews=0,
            correct_count=0,
            wrong_count=0,
            current_streak=0,
        )
        db.add(card)
        created_cards.append(card)

    db.commit()
    return created_cards


def get_due_cards(
    db: Session, student_id: uuid.UUID, limit: int = 20
) -> list[LeitnerCard]:
    """
    Returns cards where next_review_date <= today, ordered by box ASC (prioritize lower boxes),
    then by last_reviewed_at ASC.

    Eager-loads the associated QuranWord.

    Args:
        db: Database session
        student_id: UUID of the student
        limit: Maximum number of cards to return

    Returns:
        List of LeitnerCard objects ready for review
    """
    today = date.today()

    cards = db.query(LeitnerCard).filter(
        LeitnerCard.student_id == student_id,
        LeitnerCard.next_review_date <= today,
    ).order_by(
        LeitnerCard.box.asc(),
        LeitnerCard.last_reviewed_at.asc(),
    ).limit(limit).all()

    return cards


def review_card(
    db: Session, card_id: uuid.UUID, is_correct: bool
) -> LeitnerCard:
    """
    Reviews a card and updates its box, next_review_date, and stats.

    If correct: move card up one box (max 5), calculate new next_review_date.
    If wrong: move card back to Box 1, set next_review_date = today.

    Updates stats: total_reviews++, correct_count/wrong_count++, current_streak.

    Args:
        db: Database session
        card_id: UUID of the card to review
        is_correct: Whether the student answered correctly

    Returns:
        Updated LeitnerCard object
    """
    today = date.today()
    now = datetime.utcnow()

    card = db.query(LeitnerCard).filter(LeitnerCard.id == card_id).first()
    if not card:
        raise ValueError(f"Card {card_id} not found")

    # Update base stats
    card.total_reviews += 1
    card.last_reviewed_at = now

    if is_correct:
        card.correct_count += 1
        card.current_streak += 1

        # Move up one box (max 5)
        if card.box < 5:
            card.box += 1

        # Calculate new next_review_date based on box
        interval_days = BOX_INTERVALS[card.box]
        card.next_review_date = today + timedelta(days=interval_days)
    else:
        card.wrong_count += 1
        card.current_streak = 0

        # Move back to Box 1
        card.box = 1
        card.next_review_date = today

    card.updated_at = now
    db.commit()

    return card


def get_student_srs_stats(db: Session, student_id: uuid.UUID) -> dict:
    """
    Returns comprehensive SRS statistics for a student.

    Returns:
        Dictionary with keys:
        - box_1_count, box_2_count, ..., box_5_count: count of cards in each box
        - total_cards: total number of cards for this student
        - mastered_count: number of cards in box >= 4
        - due_today_count: number of cards due for review today
        - accuracy_percent: percentage of correct reviews
    """
    today = date.today()

    # Count cards by box
    box_counts = {}
    for box_num in range(1, 6):
        count = db.query(LeitnerCard).filter(
            LeitnerCard.student_id == student_id,
            LeitnerCard.box == box_num,
        ).count()
        box_counts[f"box_{box_num}_count"] = count

    # Total cards
    total_cards = db.query(LeitnerCard).filter(
        LeitnerCard.student_id == student_id,
    ).count()

    # Mastered cards (box >= 4)
    mastered_count = db.query(LeitnerCard).filter(
        LeitnerCard.student_id == student_id,
        LeitnerCard.box >= 4,
    ).count()

    # Due today
    due_today_count = db.query(LeitnerCard).filter(
        LeitnerCard.student_id == student_id,
        LeitnerCard.next_review_date <= today,
    ).count()

    # Accuracy percent
    cards = db.query(LeitnerCard).filter(
        LeitnerCard.student_id == student_id,
    ).all()

    total_reviews = sum(card.total_reviews for card in cards)
    total_correct = sum(card.correct_count for card in cards)

    accuracy_percent = 0.0
    if total_reviews > 0:
        accuracy_percent = (total_correct / total_reviews) * 100.0

    return {
        **box_counts,
        "total_cards": total_cards,
        "mastered_count": mastered_count,
        "due_today_count": due_today_count,
        "accuracy_percent": accuracy_percent,
    }


def update_module_progress(
    db: Session, student_id: uuid.UUID, module: int
) -> StudentModuleProgress:
    """
    Updates a student's module progress based on Leitner card stats.

    Calculates:
    - items_mastered: cards in box >= 4
    - total_items: total cards for this module
    - accuracy_percent: from card stats
    - is_completed: if items_mastered >= 80% of total_items
    - Unlocks next module if current is completed

    Args:
        db: Database session
        student_id: UUID of the student
        module: Module number (1-5)

    Returns:
        Updated StudentModuleProgress object
    """
    now = datetime.utcnow()

    # Get or create module progress
    progress = db.query(StudentModuleProgress).filter(
        StudentModuleProgress.student_id == student_id,
        StudentModuleProgress.module == module,
    ).first()

    if not progress:
        progress = StudentModuleProgress(
            student_id=student_id,
            module=module,
            is_unlocked=module == 1,  # Module 1 is always unlocked
            started_at=now,
        )
        db.add(progress)

    # Get all cards for this module
    cards = db.query(LeitnerCard).join(
        QuranWord, LeitnerCard.word_id == QuranWord.id
    ).filter(
        LeitnerCard.student_id == student_id,
        QuranWord.module == module,
    ).all()

    # Calculate stats
    total_items = len(cards)
    items_mastered = sum(1 for card in cards if card.box >= 4)

    progress.total_items = total_items
    progress.items_mastered = items_mastered

    # Calculate accuracy
    total_reviews = sum(card.total_reviews for card in cards)
    total_correct = sum(card.correct_count for card in cards)

    if total_reviews > 0:
        progress.accuracy_percent = (total_correct / total_reviews) * 100.0
    else:
        progress.accuracy_percent = 0.0

    # Check if completed (80% mastered)
    if total_items > 0:
        mastery_percent = (items_mastered / total_items) * 100.0
        if mastery_percent >= 80.0 and not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = now

    progress.updated_at = now
    db.commit()

    # If this module is completed, unlock the next one
    if progress.is_completed and module < 5:
        next_module_progress = db.query(StudentModuleProgress).filter(
            StudentModuleProgress.student_id == student_id,
            StudentModuleProgress.module == module + 1,
        ).first()

        if next_module_progress:
            next_module_progress.is_unlocked = True
            next_module_progress.updated_at = now
        else:
            next_module_progress = StudentModuleProgress(
                student_id=student_id,
                module=module + 1,
                is_unlocked=True,
            )
            db.add(next_module_progress)

        db.commit()

    return progress
