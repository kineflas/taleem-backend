"""
Streak business logic — the most critical part of the app.

Rules (spec §5.5):
  At midnight for each active student:
  1. Get all tasks with due_date = yesterday
  2. No tasks → streak unchanged
  3. At least 1 COMPLETED → streak += 1
  4. JokerUsage for yesterday → streak += 1
  5. All tasks SKIPPED → streak += 1
  6. Otherwise (at least 1 MISSED, no joker, no completion) → streak = 0
  7. Update longest_streak if needed
"""
from datetime import date, timedelta
import uuid
from calendar import monthrange

from sqlalchemy.orm import Session

from ..models.streak import Streak, JokerUsage
from ..models.task import Task, TaskStatus


def _next_month_first(d: date) -> date:
    if d.month == 12:
        return date(d.year + 1, 1, 1)
    return date(d.year, d.month + 1, 1)


def init_streak_for_student(db: Session, student_id: uuid.UUID) -> Streak:
    today = date.today()
    streak = Streak(
        student_id=student_id,
        current_streak_days=0,
        longest_streak_days=0,
        last_activity_date=today,
        total_completed_tasks=0,
        jokers_total=3,
        jokers_used_this_month=0,
        jokers_reset_at=_next_month_first(today),
    )
    db.add(streak)
    return streak


def process_streak_for_student(db: Session, student_id: uuid.UUID, target_date: date) -> None:
    """Called by cron at midnight for target_date = yesterday."""
    streak = db.query(Streak).filter(Streak.student_id == student_id).first()
    if not streak:
        return

    tasks = db.query(Task).filter(
        Task.student_id == student_id,
        Task.due_date == target_date,
    ).all()

    # Rule 2: no tasks → no change
    if not tasks:
        return

    has_completed = any(t.status == TaskStatus.COMPLETED for t in tasks)
    has_missed = any(t.status == TaskStatus.MISSED for t in tasks)
    all_skipped = all(t.status == TaskStatus.SKIPPED for t in tasks)

    joker_used = db.query(JokerUsage).filter(
        JokerUsage.student_id == student_id,
        JokerUsage.used_for_date == target_date,
    ).first() is not None

    if has_completed or joker_used or all_skipped:
        streak.current_streak_days += 1
        streak.last_activity_date = target_date
        if has_completed:
            completed_count = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
            streak.total_completed_tasks += completed_count
    elif has_missed:
        streak.current_streak_days = 0

    if streak.current_streak_days > streak.longest_streak_days:
        streak.longest_streak_days = streak.current_streak_days

    # Monthly joker reset
    if date.today() >= streak.jokers_reset_at:
        streak.jokers_used_this_month = 0
        streak.jokers_reset_at = _next_month_first(date.today())

    db.commit()


def increment_streak_on_completion(db: Session, student_id: uuid.UUID) -> None:
    """Called immediately when a task is completed (optimistic streak update)."""
    streak = db.query(Streak).filter(Streak.student_id == student_id).first()
    if not streak:
        return

    today = date.today()
    yesterday = today - timedelta(days=1)

    # Only update if last activity was yesterday or today (avoid double-counting)
    if streak.last_activity_date < yesterday:
        # Streak was already broken, don't increment
        streak.current_streak_days = 1
    elif streak.last_activity_date == yesterday:
        streak.current_streak_days += 1
    # If last_activity_date == today, already counted today

    streak.last_activity_date = today
    streak.total_completed_tasks += 1

    if streak.current_streak_days > streak.longest_streak_days:
        streak.longest_streak_days = streak.current_streak_days

    db.commit()
