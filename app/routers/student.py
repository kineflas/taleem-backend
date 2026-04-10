"""
Student-facing endpoints.

Routes:
  GET  /student/tasks/today          — today's tasks
  GET  /student/tasks/agenda         — tasks for a date range
  GET  /student/streak               — streak + joker info
  GET  /student/jokers               — joker usage history
  POST /student/jokers/use           — consume a joker for J or J-1
  GET  /student/progress             — learning progress summary
  GET  /student/progress/heatmap     — heatmap data (12 months)
  POST /student/link                 — link to teacher via invitation code
  GET  /student/quran/last-task      — last Quran task (for continuity)
"""
import uuid
from datetime import date, timedelta, datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from ..core.dependencies import DB, StudentUser
from ..models.program import PillarType
from ..models.streak import Streak, JokerUsage
from ..models.task import Task, TaskStatus, TaskType
from ..models.user import TeacherStudentLink, User
from ..schemas.streak import (
    HeatmapDayOut, JokerUseRequest, JokerUsageOut, ProgressOut, StreakOut,
)
from ..schemas.task import TaskOut
from ..services.notification_service import notify_student_joker_low

router = APIRouter(prefix="/student", tags=["Student"])


# ── Today's tasks ─────────────────────────────────────────────────────────────

@router.get("/tasks/today", response_model=list[TaskOut])
def tasks_today(student: StudentUser, db: DB):
    today = date.today()
    return (
        db.query(Task)
        .filter(Task.student_id == student.id, Task.due_date == today)
        .order_by(Task.created_at)
        .all()
    )


# ── Agenda (date range) ───────────────────────────────────────────────────────

@router.get("/tasks/agenda", response_model=list[TaskOut])
def tasks_agenda(
    student: StudentUser,
    db: DB,
    from_date: date = None,
    to_date: date = None,
):
    if from_date is None:
        from_date = date.today() - timedelta(days=7)
    if to_date is None:
        to_date = date.today() + timedelta(days=30)

    # Cap range to 90 days
    if (to_date - from_date).days > 90:
        to_date = from_date + timedelta(days=90)

    return (
        db.query(Task)
        .filter(
            Task.student_id == student.id,
            Task.due_date >= from_date,
            Task.due_date <= to_date,
        )
        .order_by(Task.due_date, Task.created_at)
        .all()
    )


# ── Streak ────────────────────────────────────────────────────────────────────

@router.get("/streak", response_model=StreakOut)
def get_streak(student: StudentUser, db: DB):
    streak = db.query(Streak).filter(Streak.student_id == student.id).first()
    if not streak:
        raise HTTPException(status_code=404, detail="Streak introuvable")
    return streak


# ── Jokers ────────────────────────────────────────────────────────────────────

@router.get("/jokers", response_model=list[JokerUsageOut])
def list_jokers(student: StudentUser, db: DB):
    return (
        db.query(JokerUsage)
        .filter(JokerUsage.student_id == student.id)
        .order_by(JokerUsage.used_for_date.desc())
        .limit(90)
        .all()
    )


@router.post("/jokers/use", response_model=JokerUsageOut, status_code=status.HTTP_201_CREATED)
def use_joker(body: JokerUseRequest, student: StudentUser, db: DB):
    today = date.today()
    yesterday = today - timedelta(days=1)

    # Only J or J-1 allowed
    if body.used_for_date not in (today, yesterday):
        raise HTTPException(
            status_code=400,
            detail="Le joker ne peut être utilisé que pour aujourd'hui ou hier",
        )

    streak = db.query(Streak).filter(Streak.student_id == student.id).first()
    if not streak:
        raise HTTPException(status_code=404, detail="Streak introuvable")

    # Quota check
    if streak.jokers_left <= 0:
        raise HTTPException(
            status_code=400,
            detail="Plus de jokers disponibles ce mois-ci",
        )

    # Prevent duplicate joker for same date
    existing = db.query(JokerUsage).filter(
        JokerUsage.student_id == student.id,
        JokerUsage.used_for_date == body.used_for_date,
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Un joker a déjà été utilisé pour cette date",
        )

    # Create joker usage
    joker = JokerUsage(
        student_id=student.id,
        used_for_date=body.used_for_date,
        reason=body.reason,
        note=body.note,
    )
    db.add(joker)
    streak.jokers_used_this_month += 1
    db.flush()

    # Notify if only 1 joker remaining
    if streak.jokers_left == 1:
        notify_student_joker_low(db, student, jokers_left=1)

    db.commit()
    db.refresh(joker)
    return joker


# ── Progress ──────────────────────────────────────────────────────────────────

@router.get("/progress", response_model=ProgressOut)
def get_progress(student: StudentUser, db: DB):
    today = date.today()
    month_start = today.replace(day=1)

    completed_tasks = (
        db.query(Task)
        .filter(
            Task.student_id == student.id,
            Task.status == TaskStatus.COMPLETED,
        )
        .all()
    )

    quran_tasks = [t for t in completed_tasks if t.pillar == PillarType.QURAN]
    arabic_tasks = [t for t in completed_tasks if t.pillar == PillarType.ARABIC]

    surahs_worked = len({t.surah_number for t in quran_tasks if t.surah_number})
    verses_memorized = sum(
        (t.verse_end - t.verse_start + 1)
        for t in quran_tasks
        if t.task_type == TaskType.MEMORIZATION and t.verse_start and t.verse_end
    )
    verses_revised = sum(
        (t.verse_end - t.verse_start + 1)
        for t in quran_tasks
        if t.task_type == TaskType.REVISION and t.verse_start and t.verse_end
    )

    last_quran = sorted(quran_tasks, key=lambda t: t.due_date, reverse=True)
    last_quran_title = last_quran[0].title if last_quran else None

    last_arabic = sorted(arabic_tasks, key=lambda t: t.due_date, reverse=True)
    current_book = (
        last_arabic[0].book_ref.value if last_arabic and last_arabic[0].book_ref else None
    )
    last_arabic_title = last_arabic[0].title if last_arabic else None

    # This month
    all_month_tasks = db.query(Task).filter(
        Task.student_id == student.id,
        Task.due_date >= month_start,
        Task.due_date <= today,
    ).all()
    tasks_this_month = sum(1 for t in all_month_tasks if t.status == TaskStatus.COMPLETED)
    total_tasks_this_month = len(all_month_tasks)

    return ProgressOut(
        surahs_worked=surahs_worked,
        verses_memorized=verses_memorized,
        verses_revised=verses_revised,
        last_quran_task=last_quran_title,
        current_book=current_book,
        lessons_completed=None,
        total_lessons=None,
        last_arabic_task=last_arabic_title,
        tasks_this_month=tasks_this_month,
        total_tasks_this_month=total_tasks_this_month,
    )


# ── Heatmap ───────────────────────────────────────────────────────────────────

@router.get("/progress/heatmap", response_model=list[HeatmapDayOut])
def get_heatmap(student: StudentUser, db: DB, months: int = 12):
    months = min(months, 12)
    today = date.today()
    from_date = today - timedelta(days=months * 30)

    tasks = (
        db.query(Task)
        .filter(
            Task.student_id == student.id,
            Task.due_date >= from_date,
            Task.due_date <= today,
        )
        .all()
    )

    joker_dates = {
        j.used_for_date
        for j in db.query(JokerUsage)
        .filter(
            JokerUsage.student_id == student.id,
            JokerUsage.used_for_date >= from_date,
        )
        .all()
    }

    # Group tasks by date
    days: dict[date, list[Task]] = {}
    for t in tasks:
        days.setdefault(t.due_date, []).append(t)

    result = []
    current = from_date
    while current <= today:
        day_tasks = days.get(current, [])
        completed_count = sum(1 for t in day_tasks if t.status == TaskStatus.COMPLETED)
        has_missed = any(t.status == TaskStatus.MISSED for t in day_tasks)
        has_skipped = any(t.status == TaskStatus.SKIPPED for t in day_tasks)
        joker_used = current in joker_dates

        if day_tasks or joker_used:
            result.append(HeatmapDayOut(
                date=current,
                completed_count=completed_count,
                joker_used=joker_used,
                has_missed=has_missed,
                has_skipped=has_skipped,
            ))
        current += timedelta(days=1)

    return result


# ── Link to teacher ───────────────────────────────────────────────────────────

@router.post("/link", status_code=status.HTTP_204_NO_CONTENT)
def link_to_teacher(invitation_code: str, student: StudentUser, db: DB):
    now = datetime.now(timezone.utc)

    link = db.query(TeacherStudentLink).filter(
        TeacherStudentLink.invitation_code == invitation_code,
    ).first()

    if not link:
        raise HTTPException(status_code=404, detail="Code d'invitation invalide")

    if link.invitation_expires_at and link.invitation_expires_at.replace(tzinfo=timezone.utc) < now:
        raise HTTPException(status_code=400, detail="Code d'invitation expiré")

    if link.student_id is not None:
        raise HTTPException(status_code=400, detail="Ce code a déjà été utilisé")

    # Check not already linked to this teacher
    existing = db.query(TeacherStudentLink).filter(
        TeacherStudentLink.teacher_id == link.teacher_id,
        TeacherStudentLink.student_id == student.id,
        TeacherStudentLink.is_active == True,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Vous êtes déjà lié à cet enseignant")

    link.student_id = student.id
    link.is_active = True
    link.invitation_code = None  # invalidate code after use
    db.commit()


# ── Last Quran task (continuity) ──────────────────────────────────────────────

@router.get("/quran/last-task")
def last_quran_task(student: StudentUser, db: DB):
    task = (
        db.query(Task)
        .filter(
            Task.student_id == student.id,
            Task.pillar == PillarType.QURAN,
            Task.verse_end.isnot(None),
        )
        .order_by(Task.due_date.desc(), Task.created_at.desc())
        .first()
    )
    if not task:
        return {"last_surah_number": None, "last_verse_end": None}

    return {
        "last_surah_number": task.surah_number,
        "last_surah_name": task.surah_name,
        "last_verse_end": task.verse_end,
    }
