import uuid
from datetime import datetime, date
from sqlalchemy import String, Enum, ForeignKey, Date, DateTime, Integer, Boolean, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from ..database import Base
from .program import PillarType


class TaskType(str, enum.Enum):
    MEMORIZATION = "MEMORIZATION"
    REVISION = "REVISION"
    READING = "READING"
    GRAMMAR = "GRAMMAR"
    VOCABULARY = "VOCABULARY"


class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    MISSED = "MISSED"
    SKIPPED = "SKIPPED"


class RepeatType(str, enum.Enum):
    NONE = "NONE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    CUSTOM = "CUSTOM"


class BookRef(str, enum.Enum):
    MEDINA_T1 = "MEDINA_T1"
    MEDINA_T2 = "MEDINA_T2"
    MEDINA_T3 = "MEDINA_T3"
    NORANIA = "NORANIA"
    QAIDA_BAGHDADIYA = "QAIDA_BAGHDADIYA"
    OTHER = "OTHER"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    program_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=False)
    teacher_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    pillar: Mapped[PillarType] = mapped_column(Enum(PillarType), nullable=False)
    task_type: Mapped[TaskType] = mapped_column(Enum(TaskType), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Quran fields
    surah_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    surah_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    verse_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    verse_end: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Arabic fields
    book_ref: Mapped[BookRef | None] = mapped_column(Enum(BookRef), nullable=True)
    chapter_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chapter_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    page_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    custom_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Scheduling
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    scheduled_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    repeat_type: Mapped[RepeatType] = mapped_column(Enum(RepeatType), default=RepeatType.NONE)
    repeat_days: Mapped[list | None] = mapped_column(JSON, nullable=True)
    repeat_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    repeat_group_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)

    # Status
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.PENDING, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # Optional curriculum link (set when task is generated from a curriculum item)
    curriculum_item_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    # Relationships
    program: Mapped["Program"] = relationship("Program", back_populates="tasks")
    completion: Mapped["TaskCompletion | None"] = relationship(
        "TaskCompletion", back_populates="task", uselist=False
    )


class TaskCompletion(Base):
    __tablename__ = "task_completions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id"), unique=True, nullable=False)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    difficulty: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1=Easy 2=Medium 3=Hard
    student_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    teacher_read: Mapped[bool] = mapped_column(Boolean, default=False)
    parent_validated: Mapped[bool] = mapped_column(Boolean, default=False)
    parent_validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    task: Mapped["Task"] = relationship("Task", back_populates="completion")
