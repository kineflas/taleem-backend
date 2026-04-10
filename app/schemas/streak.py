from pydantic import BaseModel
from datetime import date, datetime
import uuid
from ..models.streak import JokerReason


class StreakOut(BaseModel):
    student_id: uuid.UUID
    current_streak_days: int
    longest_streak_days: int
    last_activity_date: date
    total_completed_tasks: int
    jokers_total: int
    jokers_used_this_month: int
    jokers_reset_at: date
    jokers_left: int

    model_config = {"from_attributes": True}


class JokerUseRequest(BaseModel):
    reason: JokerReason
    note: str | None = None
    used_for_date: date  # J or J-1 only


class JokerUsageOut(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    used_for_date: date
    reason: JokerReason
    note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class HeatmapDayOut(BaseModel):
    date: date
    completed_count: int
    joker_used: bool
    has_missed: bool
    has_skipped: bool


class ProgressOut(BaseModel):
    surahs_worked: int
    verses_memorized: int
    verses_revised: int
    last_quran_task: str | None
    current_book: str | None
    lessons_completed: int | None
    total_lessons: int | None
    last_arabic_task: str | None
    tasks_this_month: int
    total_tasks_this_month: int
