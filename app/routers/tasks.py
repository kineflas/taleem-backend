"""
Task CRUD + completion + skip endpoints.

Routes:
  POST   /tasks                      — create task(s); handles repeat up to 365 days
  GET    /tasks/{task_id}            — get single task
  PATCH  /tasks/{task_id}            — update task (teacher only)
  DELETE /tasks/{task_id}            — delete task (teacher only)
  PATCH  /tasks/{task_id}/skip       — teacher marks task as SKIPPED
  POST   /tasks/{task_id}/complete   — student completes task
"""
import uuid
from datetime import date, timedelta, datetime, timezone
from typing import Literal

from fastapi import APIRouter, HTTPException, status as http_status
from sqlalchemy.orm import Session

from ..core.dependencies import CurrentUser, DB, TeacherUser, StudentUser
from ..core.security import verify_parent_token
from ..models.notification import Notification, NotificationType
from ..models.program import Program, PillarType
from ..models.task import Task, TaskStatus, TaskCompletion, RepeatType
from ..models.user import User, UserRole, TeacherStudentLink
from ..schemas.task import TaskCreate, TaskUpdate, TaskOut, TaskCompletionCreate, TaskCompletionOut
from ..services.notification_service import notify_teacher_difficulty
from ..services.streak_service import increment_streak_on_completion

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def _get_or_create_program(db: Session, teacher_id: uuid.UUID, student_id: uuid.UUID, pillar) -> Program:
    """Get active program or create a default one."""
    program = db.query(Program).filter(
        Program.teacher_id == teacher_id,
        Program.student_id == student_id,
        Program.pillar == pillar,
    ).first()
    if not program:
        program = Program(
            teacher_id=teacher_id,
            student_id=student_id,
            title=f"Programme {pillar.value.capitalize()}",
            pillar=pillar,
        )
        db.add(program)
        db.flush()
    return program


def _assert_teacher_owns(task: Task, teacher_id: uuid.UUID) -> None:
    if task.teacher_id != teacher_id:
        raise HTTPException(status_code=403, detail="Non autorisé")


def _generate_repeat_dates(body: TaskCreate, base_date: date) -> list[date]:
    """Generate all due_dates for a repeating task."""
    dates = [base_date]
    if body.repeat_type == RepeatType.NONE:
        return dates

    repeat_until = body.repeat_until or (base_date + timedelta(days=365))
    current = base_date

    if body.repeat_type == RepeatType.DAILY:
        while True:
            current += timedelta(days=1)
            if current > repeat_until:
                break
            dates.append(current)

    elif body.repeat_type == RepeatType.WEEKLY:
        while True:
            current += timedelta(days=7)
            if current > repeat_until:
                break
            dates.append(current)

    elif body.repeat_type == RepeatType.CUSTOM:
        # repeat_days: list of weekday numbers (0=Mon ... 6=Sun)
        allowed = set(body.repeat_days or [])
        if not allowed:
            return dates
        current = base_date + timedelta(days=1)
        while current <= repeat_until:
            if current.weekday() in allowed:
                dates.append(current)
            current += timedelta(days=1)

    return dates[:365]  # hard cap


# ── Create ────────────────────────────────────────────────────────────────────

@router.post("", response_model=list[TaskOut], status_code=http_status.HTTP_201_CREATED)
def create_tasks(body: TaskCreate, teacher: TeacherUser, db: DB):
    # Verify teacher-student link
    link = db.query(TeacherStudentLink).filter(
        TeacherStudentLink.teacher_id == teacher.id,
        TeacherStudentLink.student_id == body.student_id,
        TeacherStudentLink.is_active == True,
    ).first()
    if not link:
        raise HTTPException(status_code=403, detail="Cet élève n'est pas dans votre liste")

    # Get or create program
    if body.program_id:
        program = db.query(Program).filter(
            Program.id == body.program_id,
            Program.teacher_id == teacher.id,
        ).first()
        if not program:
            raise HTTPException(status_code=404, detail="Programme introuvable")
    else:
        program = _get_or_create_program(db, teacher.id, body.student_id, body.pillar)

    # Generate all dates (handles repeating tasks)
    dates = _generate_repeat_dates(body, body.due_date)
    repeat_group_id = uuid.uuid4() if len(dates) > 1 else None

    created = []
    for d in dates:
        task = Task(
            program_id=program.id,
            teacher_id=teacher.id,
            student_id=body.student_id,
            pillar=body.pillar,
            task_type=body.task_type,
            title=body.title,
            description=body.description,
            surah_number=body.surah_number,
            surah_name=body.surah_name,
            verse_start=body.verse_start,
            verse_end=body.verse_end,
            book_ref=body.book_ref,
            chapter_number=body.chapter_number,
            chapter_title=body.chapter_title,
            page_start=body.page_start,
            page_end=body.page_end,
            custom_ref=body.custom_ref,
            due_date=d,
            scheduled_date=body.scheduled_date,
            repeat_type=body.repeat_type,
            repeat_days=body.repeat_days,
            repeat_until=body.repeat_until,
            repeat_group_id=repeat_group_id,
        )
        db.add(task)
        created.append(task)

    db.flush()

    # Notify student of new task (only first occurrence)
    student = db.query(User).filter(User.id == body.student_id).first()
    if student:
        from ..services.notification_service import notify_student_new_task
        notify_student_new_task(db, student, body.title, created[0].id)

    db.commit()
    for t in created:
        db.refresh(t)
    return created


# ── Read ──────────────────────────────────────────────────────────────────────

@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: uuid.UUID, current_user: CurrentUser, db: DB):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tâche introuvable")
    if current_user.role == UserRole.TEACHER and task.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Non autorisé")
    if current_user.role == UserRole.STUDENT and task.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Non autorisé")
    return task


# ── Update ────────────────────────────────────────────────────────────────────

@router.patch("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: uuid.UUID,
    body: TaskUpdate,
    teacher: TeacherUser,
    db: DB,
    scope: Literal["this", "following", "all"] = "this",
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tâche introuvable")
    _assert_teacher_owns(task, teacher.id)

    target_tasks = [task]

    if scope != "this" and task.repeat_group_id:
        q = db.query(Task).filter(Task.repeat_group_id == task.repeat_group_id)
        if scope == "following":
            q = q.filter(Task.due_date >= task.due_date)
        target_tasks = q.all()

    for t in target_tasks:
        if body.title is not None:
            t.title = body.title
        if body.description is not None:
            t.description = body.description
        if body.due_date is not None and scope == "this":
            t.due_date = body.due_date
        if body.status is not None:
            t.status = body.status

    db.commit()
    db.refresh(task)
    return task


# ── Delete ────────────────────────────────────────────────────────────────────

@router.delete("/{task_id}", status_code=http_status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: uuid.UUID,
    teacher: TeacherUser,
    db: DB,
    scope: Literal["this", "following", "all"] = "this",
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tâche introuvable")
    _assert_teacher_owns(task, teacher.id)

    target_tasks = [task]

    if scope != "this" and task.repeat_group_id:
        q = db.query(Task).filter(Task.repeat_group_id == task.repeat_group_id)
        if scope == "following":
            q = q.filter(Task.due_date >= task.due_date)
        target_tasks = q.all()

    for t in target_tasks:
        db.delete(t)
    db.commit()


# ── Skip (teacher) ────────────────────────────────────────────────────────────

@router.patch("/{task_id}/skip", response_model=TaskOut)
def skip_task(task_id: uuid.UUID, teacher: TeacherUser, db: DB):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tâche introuvable")
    _assert_teacher_owns(task, teacher.id)
    if task.status != TaskStatus.PENDING:
        raise HTTPException(status_code=400, detail="Seules les tâches PENDING peuvent être skippées")

    task.status = TaskStatus.SKIPPED
    db.commit()
    db.refresh(task)
    return task


# ── Complete (student) ────────────────────────────────────────────────────────

@router.post("/{task_id}/complete", response_model=TaskCompletionOut)
def complete_task(task_id: uuid.UUID, body: TaskCompletionCreate, student: StudentUser, db: DB):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tâche introuvable")
    if task.student_id != student.id:
        raise HTTPException(status_code=403, detail="Non autorisé")
    if task.status == TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Tâche déjà complétée")

    # Parental validation: if child profile, require parent_token
    parent_validated = False
    parent_validated_at = None

    if student.is_child_profile:
        if not body.parent_token:
            raise HTTPException(
                status_code=403,
                detail="La validation parentale est requise pour ce profil enfant",
            )
        if not verify_parent_token(body.parent_token, str(task_id)):
            raise HTTPException(status_code=403, detail="Token parental invalide ou expiré")
        parent_validated = True
        parent_validated_at = datetime.now(timezone.utc)

    task.status = TaskStatus.COMPLETED

    completion = TaskCompletion(
        task_id=task.id,
        student_id=student.id,
        difficulty=body.difficulty,
        student_note=body.student_note,
        parent_validated=parent_validated,
        parent_validated_at=parent_validated_at,
    )
    db.add(completion)
    db.flush()

    # Optimistic streak update
    increment_streak_on_completion(db, student.id)

    # Notify teacher if difficulty = 3
    if body.difficulty == 3:
        teacher = db.query(User).filter(User.id == task.teacher_id).first()
        if teacher:
            notify_teacher_difficulty(db, teacher, student.full_name, task.title, task.id)

    db.commit()
    db.refresh(completion)
    return completion
