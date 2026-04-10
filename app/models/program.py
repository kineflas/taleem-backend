import uuid
from datetime import datetime, date
from sqlalchemy import String, Enum, ForeignKey, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from ..database import Base


class PillarType(str, enum.Enum):
    QURAN = "QURAN"
    ARABIC = "ARABIC"
    BOTH = "BOTH"


class ProgramStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"


class Program(Base):
    __tablename__ = "programs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    pillar: Mapped[PillarType] = mapped_column(Enum(PillarType), nullable=False)
    status: Mapped[ProgramStatus] = mapped_column(Enum(ProgramStatus), default=ProgramStatus.ACTIVE)
    started_at: Mapped[date] = mapped_column(Date, default=date.today)
    target_end_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="program")
