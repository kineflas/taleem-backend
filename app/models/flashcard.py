import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Text, ForeignKey, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import UniqueConstraint

from ..database import Base


class FlashcardCard(Base):
    __tablename__ = "flashcard_cards"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lesson_number: Mapped[int] = mapped_column(Integer, nullable=False)
    part_number: Mapped[int] = mapped_column(Integer, nullable=False)
    card_id_str: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    front_ar: Mapped[str] = mapped_column(Text, nullable=False)
    back_fr: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    arabic_example: Mapped[str | None] = mapped_column(Text, nullable=True)
    french_example: Mapped[str | None] = mapped_column(Text, nullable=True)
    audio_key: Mapped[str | None] = mapped_column(String(200), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    progress: Mapped[list["FlashcardProgress"]] = relationship(
        "FlashcardProgress", back_populates="card"
    )


class FlashcardProgress(Base):
    __tablename__ = "flashcard_progress"
    __table_args__ = (UniqueConstraint("student_id", "card_id", name="uq_flashcard_student_card"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    card_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("flashcard_cards.id"), nullable=False
    )
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)
    interval_days: Mapped[int] = mapped_column(Integer, default=0)
    repetitions: Mapped[int] = mapped_column(Integer, default=0)
    next_review: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    last_quality: Mapped[int | None] = mapped_column(Integer, nullable=True)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    card: Mapped["FlashcardCard"] = relationship("FlashcardCard", back_populates="progress")
