"""Pomodoro session model."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from src.core.database import Base


class SessionType(str, enum.Enum):
    """Session type."""
    WORK = "work"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"


class SessionStatus(str, enum.Enum):
    """Session status."""
    ACTIVE = "active"
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"


class PomodoroSession(Base):
    """Pomodoro session model."""
    __tablename__ = "pomodoro_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Session details
    session_type: Mapped[SessionType] = mapped_column(
        Enum(SessionType),
        nullable=False
    )
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus),
        default=SessionStatus.ACTIVE,
        nullable=False
    )

    # Duration in seconds
    planned_duration: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Timestamps
    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Optional task association
    task_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("tasks.id"),
        nullable=True
    )

    # Session number (for tracking breaks)
    session_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Interruptions count
    interruptions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<PomodoroSession {self.id}: {self.session_type} ({self.status})>"
