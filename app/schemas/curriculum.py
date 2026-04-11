from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import date, datetime
import uuid
from typing import Optional

from ..models.curriculum import (
    CurriculumType, ProgramCategory, UnitType, ItemType,
    EnrollmentMode, SubmissionStatus,
)


# ── Static content schemas ────────────────────────────────────────────────────

class CurriculumItemOut(BaseModel):
    id: uuid.UUID
    curriculum_unit_id: uuid.UUID
    item_type: ItemType
    number: int
    title_ar: str
    title_fr: str | None
    content_ar: str | None
    content_fr: str | None
    transliteration: str | None
    audio_url: str | None
    image_url: str | None
    surah_number: int | None
    verse_start: int | None
    verse_end: int | None
    letter_position: str | None
    # Serialised as 'metadata' so the Flutter model can read j['metadata']
    metadata: dict | None = Field(None, validation_alias='extra_data')
    sort_order: int

    model_config = {"from_attributes": True, "populate_by_name": True}


class CurriculumUnitOut(BaseModel):
    id: uuid.UUID
    curriculum_program_id: uuid.UUID
    unit_type: UnitType
    number: int
    title_ar: str
    title_fr: str | None
    description_fr: str | None
    audio_url: str | None
    total_items: int
    sort_order: int

    model_config = {"from_attributes": True}


class CurriculumUnitDetailOut(CurriculumUnitOut):
    items: list[CurriculumItemOut] = []


class CurriculumProgramOut(BaseModel):
    id: uuid.UUID
    curriculum_type: CurriculumType
    category: ProgramCategory
    title_ar: str
    title_fr: str
    description_fr: str | None
    total_units: int
    cover_image_url: str | None
    is_active: bool
    sort_order: int

    model_config = {"from_attributes": True}


class CurriculumProgramDetailOut(CurriculumProgramOut):
    units: list[CurriculumUnitOut] = []


# ── Enrollment schemas ────────────────────────────────────────────────────────

class EnrollRequest(BaseModel):
    curriculum_program_id: uuid.UUID
    target_end_at: date | None = None


class TeacherEnrollRequest(BaseModel):
    curriculum_program_id: uuid.UUID
    student_id: uuid.UUID
    target_end_at: date | None = None


class EnrollmentOut(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    curriculum_program_id: uuid.UUID
    teacher_id: uuid.UUID | None
    mode: EnrollmentMode
    started_at: date
    target_end_at: date | None
    current_unit_id: uuid.UUID | None
    current_item_id: uuid.UUID | None
    is_active: bool
    created_at: datetime
    program: CurriculumProgramOut

    model_config = {"from_attributes": True}


# ── Progress schemas ──────────────────────────────────────────────────────────

class ItemProgressOut(BaseModel):
    id: uuid.UUID
    curriculum_item_id: uuid.UUID
    is_completed: bool
    completed_at: datetime | None
    mastery_level: int | None
    attempt_count: int
    teacher_validated: bool
    teacher_validated_at: datetime | None

    model_config = {"from_attributes": True}


class UnitProgressOut(BaseModel):
    unit: CurriculumUnitOut
    total_items: int
    completed_items: int
    completion_pct: float
    items_progress: list[ItemProgressOut]


class EnrollmentProgressOut(BaseModel):
    enrollment: EnrollmentOut
    total_items: int
    completed_items: int
    completion_pct: float
    units: list[UnitProgressOut]


class CompleteItemRequest(BaseModel):
    mastery_level: int | None = None  # 1=seen, 2=practiced, 3=mastered


class ValidateItemRequest(BaseModel):
    student_id: uuid.UUID
    curriculum_item_id: uuid.UUID


# ── Submission schemas ────────────────────────────────────────────────────────

class SubmissionCreate(BaseModel):
    enrollment_id: uuid.UUID
    curriculum_item_id: uuid.UUID | None = None
    audio_url: str | None = None
    text_content: str | None = None


class SubmissionReviewRequest(BaseModel):
    status: SubmissionStatus
    teacher_feedback: str | None = None


class SubmissionOut(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    teacher_id: uuid.UUID | None
    enrollment_id: uuid.UUID
    curriculum_item_id: uuid.UUID | None
    audio_url: str | None
    text_content: str | None
    status: SubmissionStatus
    teacher_feedback: str | None
    reviewed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
