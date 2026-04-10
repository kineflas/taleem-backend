"""
APScheduler cron jobs.

Jobs:
  1. midnight_task_processing   — runs at 00:05 every day
     a. Mark all PENDING tasks with due_date = yesterday as MISSED
     b. For each student with tasks yesterday → run process_streak_for_student
     c. Notify teacher for each newly missed task
     d. Notify student if streak broken

  2. evening_streak_warning     — runs at 20:00 every day
     For students who have PENDING tasks today and 0 completions today
     → push "streak at risk" notification
"""
import logging
from datetime import date, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models.streak import Streak
from ..models.task import Task, TaskStatus
from ..models.user import User, UserRole
from ..services.notification_service import (
    notify_teacher_task_missed,
    notify_student_streak_broken,
    notify_student_streak_at_risk,
)
from ..services.streak_service import process_streak_for_student

logger = logging.getLogger(__name__)


def _midnight_job() -> None:
    """Mark PENDING→MISSED and run streak processing for yesterday."""
    db: Session = SessionLocal()
    try:
        yesterday = date.today() - timedelta(days=1)

        # 1. Fetch all PENDING tasks from yesterday
        pending_tasks = (
            db.query(Task)
            .filter(Task.due_date == yesterday, Task.status == TaskStatus.PENDING)
            .all()
        )

        # Mark them MISSED
        missed_by_student: dict = {}
        for task in pending_tasks:
            task.status = TaskStatus.MISSED
            missed_by_student.setdefault(task.student_id, []).append(task)

        db.flush()

        # 2. Notify teachers for each missed task
        for student_id, tasks in missed_by_student.items():
            teacher_cache: dict = {}
            for task in tasks:
                teacher_id = task.teacher_id
                if teacher_id not in teacher_cache:
                    teacher_cache[teacher_id] = db.query(User).filter(User.id == teacher_id).first()
                teacher = teacher_cache.get(teacher_id)
                student = db.query(User).filter(User.id == student_id).first()
                if teacher and student:
                    notify_teacher_task_missed(db, teacher, student.full_name, task.title, task.id)

        db.commit()

        # 3. Run streak processing for all affected students
        affected_student_ids = set(missed_by_student.keys())

        # Also process students who had tasks yesterday (even if completed/skipped)
        other_students = (
            db.query(Task.student_id)
            .filter(Task.due_date == yesterday)
            .distinct()
            .all()
        )
        for (sid,) in other_students:
            affected_student_ids.add(sid)

        streak_before: dict = {}
        for student_id in affected_student_ids:
            streak = db.query(Streak).filter(Streak.student_id == student_id).first()
            if streak:
                streak_before[student_id] = streak.current_streak_days

        for student_id in affected_student_ids:
            try:
                process_streak_for_student(db, student_id, yesterday)
            except Exception as exc:
                logger.error("Streak processing failed for %s: %s", student_id, exc)

        # 4. Notify students whose streak was reset
        for student_id, before in streak_before.items():
            streak = db.query(Streak).filter(Streak.student_id == student_id).first()
            if streak and streak.current_streak_days == 0 and before > 0:
                student = db.query(User).filter(User.id == student_id).first()
                if student:
                    notify_student_streak_broken(db, student)

        db.commit()
        logger.info("Midnight job complete — processed %d students", len(affected_student_ids))

    except Exception as exc:
        logger.error("Midnight job error: %s", exc)
        db.rollback()
    finally:
        db.close()


def _evening_warning_job() -> None:
    """At 20:00 — warn students who haven't completed anything today."""
    db: Session = SessionLocal()
    try:
        today = date.today()

        # Find students with pending tasks today
        student_ids_with_pending = (
            db.query(Task.student_id)
            .filter(Task.due_date == today, Task.status == TaskStatus.PENDING)
            .distinct()
            .all()
        )

        for (student_id,) in student_ids_with_pending:
            # Check if they completed anything today
            completed_today = (
                db.query(Task)
                .filter(
                    Task.student_id == student_id,
                    Task.due_date == today,
                    Task.status == TaskStatus.COMPLETED,
                )
                .count()
            )

            if completed_today == 0:
                student = db.query(User).filter(User.id == student_id).first()
                streak = db.query(Streak).filter(Streak.student_id == student_id).first()
                if student and streak and streak.current_streak_days > 0:
                    notify_student_streak_at_risk(db, student, streak.current_streak_days)

        db.commit()
        logger.info("Evening warning job complete")

    except Exception as exc:
        logger.error("Evening warning job error: %s", exc)
        db.rollback()
    finally:
        db.close()


def create_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="UTC")

    # Midnight job: 00:05 UTC every day
    scheduler.add_job(
        _midnight_job,
        trigger=CronTrigger(hour=0, minute=5),
        id="midnight_task_processing",
        replace_existing=True,
        misfire_grace_time=600,  # 10-minute grace
    )

    # Evening warning: 20:00 UTC every day
    scheduler.add_job(
        _evening_warning_job,
        trigger=CronTrigger(hour=20, minute=0),
        id="evening_streak_warning",
        replace_existing=True,
        misfire_grace_time=600,
    )

    return scheduler
