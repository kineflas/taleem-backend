"""SQLAlchemy models for L'Odyssée des Lettres progress persistence."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, DateTime, Float, Integer, String, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class OdysseeProgress(Base):
    """Per-student, per-lesson progress for L'Odyssée des Lettres."""
    __tablename__ = "odyssee_lettres_progress"
    __table_args__ = (
        UniqueConstraint("student_id", "lesson_number", name="uq_odyssee_progress"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True,
    )
    lesson_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # 7-step tracking
    current_step: Mapped[int] = mapped_column(Integer, default=0)
    ecoute_done: Mapped[bool] = mapped_column(Boolean, default=False)
    discovery_done: Mapped[bool] = mapped_column(Boolean, default=False)
    exercises_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    mini_lecture_done: Mapped[bool] = mapped_column(Boolean, default=False)
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
