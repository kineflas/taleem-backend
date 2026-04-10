"""
Teacher-facing endpoints.

Routes:
  GET  /teacher/students                    — list linked students
  POST /teacher/students/invite             — create invitation link
  GET  /teacher/students/{student_id}/overview
  POST /teacher/students/{student_id}/feedback — mark hard-feedback as read
  GET  /teacher/tasks                       — teacher's task feed
  GET  /teacher/programs                    — programs this teacher manages
  POST /teacher/programs                    — create program
"""
import random
import string
import uuid
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from ..core.dependencies import DB, TeacherUser
from ..models.notification import Notification, NotificationType
from ..models.program import Program, ProgramStatus
from ..models.streak import Streak
from ..models.task import Task, TaskStatus, TaskCompletion
from ..models.user import TeacherStudentLink, User, UserRole
from ..schemas.auth import UserOut
from ..schemas.task import (
    ProgramCreate, ProgramOut,
    StudentOverviewOut, TaskOut,
)

router = APIRouter(prefix="/teacher", tags=["Teacher"])


def _assert_linked(db: Session, teacher_id: uuid.UUID, student_id: uuid.UUID) -> None:
    link = db.query(TeacherStudentLink).filter(
        TeacherStudentLink.teacher_id == teacher_id,
        TeacherStudentLink.student_id == student_id,
        TeacherStudentLink.is_active == True,
    ).first()
    if not link:
        raise HTTPException(status_code=403, detail="Cet élève n'est pas dans votre liste")


# ── Students list ─────────────────────────────────────────────────────────────

@router.get("/students", response_model=list[StudentOverviewOut])
def list_students(teacher: TeacherUser, db: DB):
    links = db.query(TeacherStudentLink).filter(
        TeacherStudentLink.teacher_id == teacher.id,
        TeacherStudentLink.is_active == True,
        TeacherStudentLink.student_id.isnot(None),
    ).all()

    today = date.today()
    result = []

    for link in links:
        student = link.student
        if not student or not student.is_active:
            continue

        tasks_today = db.query(Task).filter(
            Task.student_id == student.id,
            Task.due_date == today,
        ).all()

        completed_today = sum(1 for t in tasks_today if t.status == TaskStatus.COMPLETED)
        pending_today = sum(1 for t in tasks_today if t.status == TaskStatus.PENDING)

        streak = db.query(Streak).filter(Streak.student_id == student.id).first()

        unread_hard = db.query(Notification).filter(
            Notification.recipient_id == teacher.id,
            Notification.type == NotificationType.STUDENT_FEEDBACK_HARD,
            Notification.is_read == False,
        ).count()

        result.append(StudentOverviewOut(
            student=UserOut.model_validate(student),
            tasks_today=len(tasks_today),
            completed_today=completed_today,
            pending_today=pending_today,
            current_streak=streak.current_streak_days if streak else 0,
            jokers_left=streak.jokers_left if streak else 0,
            unread_hard_feedback=unread_hard,
            is_child_profile=student.is_child_profile,
        ))

    return result


# ── Invite ────────────────────────────────────────────────────────────────────

@router.post("/students/invite", status_code=status.HTTP_201_CREATED)
def create_invitation(teacher: TeacherUser, db: DB):
    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    expires_at = datetime.now(timezone.utc) + timedelta(hours=48)

    link = TeacherStudentLink(
        teacher_id=teacher.id,
        student_id=None,
        invitation_code=code,
        invitation_expires_at=expires_at,
        is_active=False,  # becomes True when student accepts
    )
    db.add(link)
    db.commit()
    return {"invitation_code": code, "expires_at": expires_at}


# ── Student overview ──────────────────────────────────────────────────────────

@router.get("/students/{student_id}/overview", response_model=StudentOverviewOut)
def student_overview(student_id: uuid.UUID, teacher: TeacherUser, db: DB):
    _assert_linked(db, teacher.id, student_id)

    student = db.query(User).filter(User.id == student_id, User.is_active == True).first()
    if not student:
        raise HTTPException(status_code=404, detail="Élève introuvable")

    today = date.today()
    tasks_today = db.query(Task).filter(
        Task.student_id == student_id,
        Task.due_date == today,
    ).all()

    completed_today = sum(1 for t in tasks_today if t.status == TaskStatus.COMPLETED)
    pending_today = sum(1 for t in tasks_today if t.status == TaskStatus.PENDING)

    streak = db.query(Streak).filter(Streak.student_id == student_id).first()

    unread_hard = db.query(Notification).filter(
        Notification.recipient_id == teacher.id,
        Notification.type == NotificationType.STUDENT_FEEDBACK_HARD,
        Notification.is_read == False,
    ).count()

    return StudentOverviewOut(
        student=UserOut.model_validate(student),
        tasks_today=len(tasks_today),
        completed_today=completed_today,
        pending_today=pending_today,
        current_streak=streak.current_streak_days if streak else 0,
        jokers_left=streak.jokers_left if streak else 0,
        unread_hard_feedback=unread_hard,
        is_child_profile=student.is_child_profile,
    )


# ── Mark hard-feedback as read ────────────────────────────────────────────────

@router.post("/students/{student_id}/feedback/read", status_code=status.HTTP_204_NO_CONTENT)
def mark_feedback_read(student_id: uuid.UUID, teacher: TeacherUser, db: DB):
    _assert_linked(db, teacher.id, student_id)

    # Mark all task completions for this student as teacher_read
    completions = (
        db.query(TaskCompletion)
        .join(Task, TaskCompletion.task_id == Task.id)
        .filter(
            Task.student_id == student_id,
            Task.teacher_id == teacher.id,
            TaskCompletion.teacher_read == False,
        )
        .all()
    )
    for c in completions:
        c.teacher_read = True

    # Mark notifications as read too
    db.query(Notification).filter(
        Notification.recipient_id == teacher.id,
        Notification.type == NotificationType.STUDENT_FEEDBACK_HARD,
        Notification.is_read == False,
    ).update({"is_read": True})

    db.commit()


# ── Teacher task feed ─────────────────────────────────────────────────────────

@router.get("/tasks", response_model=list[TaskOut])
def teacher_tasks(
    teacher: TeacherUser,
    db: DB,
    student_id: uuid.UUID | None = None,
    due_date: date | None = None,
    status: TaskStatus | None = None,
):
    q = db.query(Task).filter(Task.teacher_id == teacher.id)
    if student_id:
        q = q.filter(Task.student_id == student_id)
    if due_date:
        q = q.filter(Task.due_date == due_date)
    if status:
        q = q.filter(Task.status == status)
    tasks = q.order_by(Task.due_date.desc()).limit(200).all()
    return tasks


# ── Programs ──────────────────────────────────────────────────────────────────

@router.get("/programs", response_model=list[ProgramOut])
def list_programs(teacher: TeacherUser, db: DB, student_id: uuid.UUID | None = None):
    q = db.query(Program).filter(Program.teacher_id == teacher.id)
    if student_id:
        q = q.filter(Program.student_id == student_id)
    return q.order_by(Program.created_at.desc()).all()


@router.post("/programs", response_model=ProgramOut, status_code=status.HTTP_201_CREATED)
def create_program(body: ProgramCreate, teacher: TeacherUser, db: DB):
    _assert_linked(db, teacher.id, body.student_id)

    program = Program(
        teacher_id=teacher.id,
        student_id=body.student_id,
        title=body.title,
        pillar=body.pillar,
    )
    db.add(program)
    db.commit()
    db.refresh(program)
    return program
