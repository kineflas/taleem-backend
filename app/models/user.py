import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Enum, ForeignKey, Text, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from ..database import Base


class UserRole(str, enum.Enum):
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    locale: Mapped[str] = mapped_column(String(10), default="ar")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # Parental validation
    is_child_profile: Mapped[bool] = mapped_column(Boolean, default=False)
    parent_pin_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # FCM token for push notifications
    fcm_token: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    teacher_links: Mapped[list["TeacherStudentLink"]] = relationship(
        "TeacherStudentLink",
        foreign_keys="TeacherStudentLink.teacher_id",
        back_populates="teacher",
    )
    student_links: Mapped[list["TeacherStudentLink"]] = relationship(
        "TeacherStudentLink",
        foreign_keys="TeacherStudentLink.student_id",
        back_populates="student",
    )
    streak: Mapped["Streak | None"] = relationship("Streak", back_populates="student", uselist=False)
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="recipient")

    @property
    def has_parent_pin(self) -> bool:
        return self.parent_pin_hash is not None


class TeacherStudentLink(Base):
    __tablename__ = "teacher_student_links"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    student_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    linked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    joker_quota_override: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Invitation code
    invitation_code: Mapped[str | None] = mapped_column(String(10), nullable=True, index=True)
    invitation_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    teacher: Mapped["User"] = relationship("User", foreign_keys=[teacher_id], back_populates="teacher_links")
    student: Mapped["User | None"] = relationship("User", foreign_keys=[student_id], back_populates="student_links")
