import uuid
from datetime import datetime, date
from sqlalchemy import String, Enum, ForeignKey, Date, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from ..database import Base


class JokerReason(str, enum.Enum):
    ILLNESS = "ILLNESS"
    TRAVEL = "TRAVEL"
    FAMILY = "FAMILY"
    OTHER = "OTHER"


class Streak(Base):
    __tablename__ = "streaks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    current_streak_days: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak_days: Mapped[int] = mapped_column(Integer, default=0)
    last_activity_date: Mapped[date] = mapped_column(Date, default=date.today)
    total_completed_tasks: Mapped[int] = mapped_column(Integer, default=0)
    jokers_total: Mapped[int] = mapped_column(Integer, default=3)
    jokers_used_this_month: Mapped[int] = mapped_column(Integer, default=0)
    jokers_reset_at: Mapped[date] = mapped_column(Date, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    student: Mapped["User"] = relationship("User", back_populates="streak")

    @property
    def jokers_left(self) -> int:
        return max(0, self.jokers_total - self.jokers_used_this_month)


class JokerUsage(Base):
    __tablename__ = "joker_usages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    used_for_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[JokerReason] = mapped_column(Enum(JokerReason), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
