"""
Curriculum Engine models — the 5 learning programs.

Architecture:
  CurriculumProgram → CurriculumUnit → CurriculumItem  (static content)
  StudentEnrollment → StudentItemProgress              (per-student progress)
  StudentSubmission                                    (audio/text submissions)
"""
import uuid
import enum
from datetime import datetime, date
from typing import Optional

from sqlalchemy import (
    String, Text, Integer, Boolean, Date, DateTime,
    Enum, ForeignKey, JSON, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base


# ── Enums ─────────────────────────────────────────────────────────────────────

class CurriculumType(str, enum.Enum):
    ALPHABET_ARABE  = "ALPHABET_ARABE"
    QAIDA_NOURANIA  = "QAIDA_NOURANIA"
    MEDINE_T1       = "MEDINE_T1"
    TAJWID          = "TAJWID"
    HIFZ_REVISION   = "HIFZ_REVISION"


class UnitType(str, enum.Enum):
    CHAPTER         = "CHAPTER"
    MODULE          = "MODULE"
    LESSON          = "LESSON"
    LETTER          = "LETTER"
    JUZ             = "JUZ"


class ItemType(str, enum.Enum):
    LETTER_FORM     = "LETTER_FORM"
    COMBINATION     = "COMBINATION"
    RULE            = "RULE"
    VOCABULARY      = "VOCABULARY"
    GRAMMAR_POINT   = "GRAMMAR_POINT"
    SURAH_SEGMENT   = "SURAH_SEGMENT"
    EXAMPLE         = "EXAMPLE"


class EnrollmentMode(str, enum.Enum):
    TEACHER_ASSIGNED    = "TEACHER_ASSIGNED"
    STUDENT_AUTONOMOUS  = "STUDENT_AUTONOMOUS"


class SubmissionStatus(str, enum.Enum):
    PENDING_REVIEW      = "PENDING_REVIEW"
    APPROVED            = "APPROVED"
    NEEDS_IMPROVEMENT   = "NEEDS_IMPROVEMENT"
    REJECTED            = "REJECTED"


# ── Static content tables ─────────────────────────────────────────────────────

class CurriculumProgram(Base):
    __tablename__ = "curriculum_programs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    curriculum_type: Mapped[CurriculumType] = mapped_column(
        Enum(CurriculumType), unique=True, nullable=False
    )
    title_ar: Mapped[str] = mapped_column(String(255), nullable=False)
    title_fr: Mapped[str] = mapped_column(String(255), nullable=False)
    description_fr: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_units: Mapped[int] = mapped_column(Integer, default=0)
    cover_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    units: Mapped[list["CurriculumUnit"]] = relationship(
        "CurriculumUnit", back_populates="program", order_by="CurriculumUnit.sort_order"
    )
    enrollments: Mapped[list["StudentEnrollment"]] = relationship(
        "StudentEnrollment", back_populates="program"
    )


class CurriculumUnit(Base):
    __tablename__ = "curriculum_units"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    curriculum_program_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_programs.id"), nullable=False, index=True
    )
    unit_type: Mapped[UnitType] = mapped_column(Enum(UnitType), nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    title_ar: Mapped[str] = mapped_column(String(255), nullable=False)
    title_fr: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description_fr: Mapped[str | None] = mapped_column(Text, nullable=True)
    audio_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    total_items: Mapped[int] = mapped_column(Integer, default=0)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    program: Mapped["CurriculumProgram"] = relationship("CurriculumProgram", back_populates="units")
    items: Mapped[list["CurriculumItem"]] = relationship(
        "CurriculumItem", back_populates="unit", order_by="CurriculumItem.sort_order"
    )


class CurriculumItem(Base):
    __tablename__ = "curriculum_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    curriculum_unit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_units.id"), nullable=False, index=True
    )
    item_type: Mapped[ItemType] = mapped_column(Enum(ItemType), nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Content fields
    title_ar: Mapped[str] = mapped_column(String(500), nullable=False)
    title_fr: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content_ar: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_fr: Mapped[str | None] = mapped_column(Text, nullable=True)
    transliteration: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Media
    audio_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Quran references (HIFZ_REVISION items)
    surah_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    verse_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    verse_end: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Letter forms (ALPHABET items)
    letter_position: Mapped[str | None] = mapped_column(String(20), nullable=True)  # isolated/initial/medial/final

    # Extra structured data (makharij coords, examples list, etc.)
    metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    unit: Mapped["CurriculumUnit"] = relationship("CurriculumUnit", back_populates="items")
    progress_records: Mapped[list["StudentItemProgress"]] = relationship(
        "StudentItemProgress", back_populates="item"
    )
    submissions: Mapped[list["StudentSubmission"]] = relationship(
        "StudentSubmission", back_populates="item"
    )


# ── Progress tables ───────────────────────────────────────────────────────────

class StudentEnrollment(Base):
    __tablename__ = "student_enrollments"
    __table_args__ = (
        UniqueConstraint("student_id", "curriculum_program_id", name="uq_enrollment_student_program"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    curriculum_program_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_programs.id"), nullable=False
    )
    teacher_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    mode: Mapped[EnrollmentMode] = mapped_column(
        Enum(EnrollmentMode), default=EnrollmentMode.STUDENT_AUTONOMOUS
    )
    started_at: Mapped[date] = mapped_column(Date, default=date.today)
    target_end_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Progression pointer (updated as student advances)
    current_unit_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_units.id"), nullable=True
    )
    current_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_items.id"), nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    student: Mapped["User"] = relationship("User", foreign_keys=[student_id])
    teacher: Mapped["User | None"] = relationship("User", foreign_keys=[teacher_id])
    program: Mapped["CurriculumProgram"] = relationship("CurriculumProgram", back_populates="enrollments")
    current_unit: Mapped["CurriculumUnit | None"] = relationship("CurriculumUnit", foreign_keys=[current_unit_id])
    current_item: Mapped["CurriculumItem | None"] = relationship("CurriculumItem", foreign_keys=[current_item_id])
    item_progress: Mapped[list["StudentItemProgress"]] = relationship(
        "StudentItemProgress", back_populates="enrollment"
    )
    submissions: Mapped[list["StudentSubmission"]] = relationship(
        "StudentSubmission", back_populates="enrollment"
    )


class StudentItemProgress(Base):
    __tablename__ = "student_item_progress"
    __table_args__ = (
        UniqueConstraint("enrollment_id", "curriculum_item_id", name="uq_item_progress"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    enrollment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("student_enrollments.id"), nullable=False, index=True
    )
    # Denormalized for fast queries
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    curriculum_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_items.id"), nullable=False
    )

    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    mastery_level: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1=seen, 2=practiced, 3=mastered
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    last_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    teacher_validated: Mapped[bool] = mapped_column(Boolean, default=False)
    teacher_validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    enrollment: Mapped["StudentEnrollment"] = relationship("StudentEnrollment", back_populates="item_progress")
    item: Mapped["CurriculumItem"] = relationship("CurriculumItem", back_populates="progress_records")


class StudentSubmission(Base):
    __tablename__ = "student_submissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    teacher_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    enrollment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("student_enrollments.id"), nullable=False
    )
    curriculum_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("curriculum_items.id"), nullable=True
    )
    # Optional link to existing Task system
    task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True
    )

    audio_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    text_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[SubmissionStatus] = mapped_column(
        Enum(SubmissionStatus), default=SubmissionStatus.PENDING_REVIEW, index=True
    )
    teacher_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    student: Mapped["User"] = relationship("User", foreign_keys=[student_id])
    teacher: Mapped["User | None"] = relationship("User", foreign_keys=[teacher_id])
    enrollment: Mapped["StudentEnrollment"] = relationship("StudentEnrollment", back_populates="submissions")
    item: Mapped["CurriculumItem | None"] = relationship("CurriculumItem", back_populates="submissions")
