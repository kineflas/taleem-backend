import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Text, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base


class DiagnosticQuestion(Base):
    __tablename__ = "diagnostic_questions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pool: Mapped[str] = mapped_column(String(1), nullable=False)  # A, B, C
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False)  # 1, 2, 3
    skill_tested: Mapped[str] = mapped_column(String(100), nullable=False)
    lesson_ref: Mapped[str | None] = mapped_column(String(20), nullable=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[list] = mapped_column(JSON, nullable=False)
    correct: Mapped[int] = mapped_column(Integer, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    adaptive_hint: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)



class DiagnosticSession(Base):
    __tablename__ = "diagnostic_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    answers: Mapped[list | None] = mapped_column(JSON, nullable=True)
    current_pool: Mapped[str] = mapped_column(String(1), default="A")
    current_pool_index: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    result: Mapped["DiagnosticResult | None"] = relationship(
        "DiagnosticResult", back_populates="session", uselist=False
    )


class DiagnosticResult(Base):
    __tablename__ = "diagnostic_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("diagnostic_sessions.id"), unique=True, nullable=False
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    level: Mapped[str] = mapped_column(String(50), nullable=False)
    level_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    skill_scores: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    recommended_path: Mapped[list | None] = mapped_column(JSON, nullable=True)
    estimated_duration: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    session: Mapped["DiagnosticSession"] = relationship("DiagnosticSession", back_populates="result")
