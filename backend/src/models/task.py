"""Task model for task management."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column
import enum
from src.core.database import Base


class TaskPriority(str, enum.Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, enum.Enum):
    """Task status."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Task(Base):
    """Task model."""
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus),
        default=TaskStatus.TODO,
        nullable=False
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority),
        default=TaskPriority.MEDIUM,
        nullable=False
    )

    # Pomodoro tracking
    estimated_pomodoros: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    completed_pomodoros: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Optional GitHub integration
    github_issue_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Optional tags
    tags: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # JSON string

    def __repr__(self) -> str:
        return f"<Task {self.id}: {self.title} ({self.status})>"
