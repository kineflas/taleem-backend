"""SQLAlchemy models for Médine Tome 1 — V2 progress persistence."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, DateTime, Float, Integer, String, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class MedineV2Progress(Base):
    """Per-student, per-lesson progress for Médine Tome 1 V2."""
    __tablename__ = "medine_v2_progress"
    __table_args__ = (
        UniqueConstraint("student_id", "lesson_number", name="uq_medine_v2_progress"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True,
    )
    lesson_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Step tracking
    current_step: Mapped[int] = mapped_column(Integer, default=0)
    discovery_done: Mapped[bool] = mapped_column(Boolean, default=False)
    dialogue_done: Mapped[bool] = mapped_column(Boolean, default=False)
    exercises_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    quiz_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Gamification
    stars: Mapped[int] = mapped_column(Integer, default=0)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
