from pydantic import BaseModel, model_validator
from datetime import date, datetime
import uuid
from typing import Any

from ..models.task import TaskType, TaskStatus, RepeatType, BookRef
from ..models.program import PillarType, ProgramStatus


# ─── Program ─────────────────────────────────────────────────────────────────

class ProgramCreate(BaseModel):
    student_id: uuid.UUID
    title: str
    pillar: PillarType


class ProgramOut(BaseModel):
    id: uuid.UUID
    teacher_id: uuid.UUID
    student_id: uuid.UUID
    title: str
    pillar: PillarType
    status: ProgramStatus
    started_at: date
    target_end_at: date | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Task ────────────────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    student_id: uuid.UUID
    program_id: uuid.UUID | None = None  # Auto-create if None
    pillar: PillarType
    task_type: TaskType
    title: str
    description: str | None = None

    # Quran
    surah_number: int | None = None
    surah_name: str | None = None
    verse_start: int | None = None
    verse_end: int | None = None

    # Arabic
    book_ref: BookRef | None = None
    chapter_number: int | None = None
    chapter_title: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    custom_ref: str | None = None

    # Schedule
    due_date: date
    scheduled_date: date | None = None
    repeat_type: RepeatType = RepeatType.NONE
    repeat_days: list[int] | None = None
    repeat_until: date | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_date: date | None = None
    status: TaskStatus | None = None


class TaskCompletionCreate(BaseModel):
    difficulty: int | None = None  # 1, 2, or 3
    student_note: str | None = None
    parent_token: str | None = None

    @model_validator(mode="after")
    def validate_difficulty(self) -> "TaskCompletionCreate":
        if self.difficulty is not None and self.difficulty not in (1, 2, 3):
            raise ValueError("La difficulté doit être 1, 2 ou 3")
        return self


class TaskCompletionOut(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    student_id: uuid.UUID
    completed_at: datetime
    difficulty: int | None
    student_note: str | None
    teacher_read: bool
    parent_validated: bool
    parent_validated_at: datetime | None

    model_config = {"from_attributes": True}


class SurahOut(BaseModel):
    surah_number: int
    surah_name_ar: str
    surah_name_fr: str
    surah_name_en: str
    total_verses: int
    juz_number: int
    is_meccan: bool

    model_config = {"from_attributes": True}


class TaskOut(BaseModel):
    id: uuid.UUID
    program_id: uuid.UUID
    teacher_id: uuid.UUID
    student_id: uuid.UUID
    pillar: PillarType
    task_type: TaskType
    title: str
    description: str | None
    surah_number: int | None
    surah_name: str | None
    verse_start: int | None
    verse_end: int | None
    book_ref: BookRef | None
    chapter_number: int | None
    chapter_title: str | None
    page_start: int | None
    page_end: int | None
    custom_ref: str | None
    due_date: date
    scheduled_date: date | None
    repeat_type: RepeatType
    status: TaskStatus
    created_at: datetime
    completion: TaskCompletionOut | None

    model_config = {"from_attributes": True}


# ─── Student overview (for teacher dashboard) ────────────────────────────────

class StudentOverviewOut(BaseModel):
    student: Any  # UserOut
    tasks_today: int
    completed_today: int
    pending_today: int
    current_streak: int
    jokers_left: int
    unread_hard_feedback: int
    is_child_profile: bool
