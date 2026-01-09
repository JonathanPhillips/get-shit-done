"""Pomodoro session schemas for API requests and responses."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from src.models.pomodoro import SessionType, SessionStatus


class PomodoroSessionCreate(BaseModel):
    """Schema for creating a Pomodoro session."""
    session_type: SessionType
    planned_duration: int = Field(..., ge=60, description="Duration in seconds")
    task_id: Optional[int] = None
    session_number: int = Field(default=1, ge=1)


class PomodoroSessionUpdate(BaseModel):
    """Schema for updating a Pomodoro session."""
    status: Optional[SessionStatus] = None
    actual_duration: Optional[int] = Field(None, ge=0)
    ended_at: Optional[datetime] = None
    notes: Optional[str] = None
    interruptions: Optional[int] = Field(None, ge=0)


class PomodoroSessionResponse(BaseModel):
    """Schema for Pomodoro session response."""
    id: int
    session_type: SessionType
    status: SessionStatus
    planned_duration: int
    actual_duration: Optional[int] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    task_id: Optional[int] = None
    session_number: int
    notes: Optional[str] = None
    interruptions: int

    class Config:
        from_attributes = True


class PomodoroSessionListResponse(BaseModel):
    """Schema for list of Pomodoro sessions."""
    sessions: List[PomodoroSessionResponse]
    total: int


class PomodoroStatsResponse(BaseModel):
    """Schema for Pomodoro statistics."""
    total_sessions: int
    completed_sessions: int
    total_work_time: int  # in seconds
    total_break_time: int  # in seconds
    average_session_duration: float
    interruptions_count: int
    today_sessions: int
    today_work_time: int
    current_streak: int
