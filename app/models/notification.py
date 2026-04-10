import uuid
from datetime import datetime
from sqlalchemy import String, Enum, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from ..database import Base


class NotificationType(str, enum.Enum):
    TASK_DUE = "TASK_DUE"
    TASK_MISSED = "TASK_MISSED"
    STUDENT_FEEDBACK_HARD = "STUDENT_FEEDBACK_HARD"
    STREAK_AT_RISK = "STREAK_AT_RISK"
    PROGRAM_UPDATE = "PROGRAM_UPDATE"
    JOKER_LOW = "JOKER_LOW"
    NEW_TASK_ASSIGNED = "NEW_TASK_ASSIGNED"
    STREAK_BROKEN = "STREAK_BROKEN"
    SUBMISSION_RECEIVED = "SUBMISSION_RECEIVED"
    SUBMISSION_REVIEWED = "SUBMISSION_REVIEWED"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    related_task_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    recipient: Mapped["User"] = relationship("User", back_populates="notifications")
