"""Task schemas for API requests and responses."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from src.models.task import TaskPriority, TaskStatus


class TaskBase(BaseModel):
    """Base task schema."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    estimated_pomodoros: int = Field(default=1, ge=1)
    tags: Optional[str] = None
    github_issue_url: Optional[str] = None


class TaskCreate(TaskBase):
    """Schema for creating a task."""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    estimated_pomodoros: Optional[int] = Field(None, ge=1)
    completed_pomodoros: Optional[int] = Field(None, ge=0)
    tags: Optional[str] = None
    github_issue_url: Optional[str] = None


class TaskResponse(TaskBase):
    """Schema for task response."""
    id: int
    status: TaskStatus
    completed_pomodoros: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for list of tasks."""
    tasks: List[TaskResponse]
    total: int
