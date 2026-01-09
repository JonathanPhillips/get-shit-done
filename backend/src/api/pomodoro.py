"""Pomodoro timer API endpoints."""
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from src.core.database import get_db
from src.models.pomodoro import PomodoroSession, SessionType, SessionStatus
from src.schemas.pomodoro import (
    PomodoroSessionCreate,
    PomodoroSessionUpdate,
    PomodoroSessionResponse,
    PomodoroSessionListResponse,
    PomodoroStatsResponse,
)

router = APIRouter(prefix="/pomodoro", tags=["pomodoro"])


@router.get("/sessions", response_model=PomodoroSessionListResponse)
async def list_sessions(
    status: Optional[SessionStatus] = None,
    task_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """
    List Pomodoro sessions with optional filtering.

    - **status**: Filter by session status
    - **task_id**: Filter by associated task
    - **skip**: Number of sessions to skip (pagination)
    - **limit**: Maximum number of sessions to return
    """
    query = select(PomodoroSession)

    conditions = []
    if status:
        conditions.append(PomodoroSession.status == status)
    if task_id:
        conditions.append(PomodoroSession.task_id == task_id)

    if conditions:
        query = query.where(and_(*conditions))

    # Get total count
    count_query = select(func.count()).select_from(PomodoroSession)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Get sessions
    query = query.offset(skip).limit(limit).order_by(PomodoroSession.started_at.desc())
    result = await db.execute(query)
    sessions = result.scalars().all()

    return PomodoroSessionListResponse(sessions=sessions, total=total)


@router.get("/sessions/{session_id}", response_model=PomodoroSessionResponse)
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific Pomodoro session by ID."""
    query = select(PomodoroSession).where(PomodoroSession.id == session_id)
    result = await db.execute(query)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return session


@router.get("/active", response_model=Optional[PomodoroSessionResponse])
async def get_active_session(
    db: AsyncSession = Depends(get_db),
):
    """Get the currently active Pomodoro session, if any."""
    query = select(PomodoroSession).where(
        PomodoroSession.status == SessionStatus.ACTIVE
    ).order_by(PomodoroSession.started_at.desc())
    result = await db.execute(query)
    session = result.scalars().first()

    return session


@router.post("/sessions", response_model=PomodoroSessionResponse, status_code=201)
async def start_session(
    session_data: PomodoroSessionCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Start a new Pomodoro session.

    Automatically marks any active sessions as interrupted before starting new one.
    """
    # Check for existing active sessions (may be multiple due to data corruption)
    active_query = select(PomodoroSession).where(
        PomodoroSession.status == SessionStatus.ACTIVE
    )
    active_result = await db.execute(active_query)
    active_sessions = active_result.scalars().all()

    # Interrupt all active sessions
    for active_session in active_sessions:
        active_session.status = SessionStatus.INTERRUPTED
        active_session.ended_at = datetime.utcnow()
        active_session.actual_duration = int(
            (active_session.ended_at - active_session.started_at).total_seconds()
        )

    # Create new session
    session = PomodoroSession(**session_data.model_dump())
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.patch("/sessions/{session_id}", response_model=PomodoroSessionResponse)
async def update_session(
    session_id: int,
    session_data: PomodoroSessionUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a Pomodoro session."""
    query = select(PomodoroSession).where(PomodoroSession.id == session_id)
    result = await db.execute(query)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Update fields
    update_data = session_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(session, field, value)

    await db.commit()
    await db.refresh(session)
    return session


@router.post("/sessions/{session_id}/complete", response_model=PomodoroSessionResponse)
async def complete_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Mark a Pomodoro session as completed."""
    query = select(PomodoroSession).where(PomodoroSession.id == session_id)
    result = await db.execute(query)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = SessionStatus.COMPLETED
    session.ended_at = datetime.utcnow()
    session.actual_duration = int(
        (session.ended_at - session.started_at).total_seconds()
    )

    await db.commit()
    await db.refresh(session)
    return session


@router.post("/sessions/{session_id}/interrupt", response_model=PomodoroSessionResponse)
async def interrupt_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Mark a Pomodoro session as interrupted."""
    query = select(PomodoroSession).where(PomodoroSession.id == session_id)
    result = await db.execute(query)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = SessionStatus.INTERRUPTED
    session.ended_at = datetime.utcnow()
    session.actual_duration = int(
        (session.ended_at - session.started_at).total_seconds()
    )
    session.interruptions += 1

    await db.commit()
    await db.refresh(session)
    return session


@router.get("/stats", response_model=PomodoroStatsResponse)
async def get_stats(
    db: AsyncSession = Depends(get_db),
):
    """Get Pomodoro session statistics."""
    # Total sessions
    total_query = select(func.count()).select_from(PomodoroSession)
    total_result = await db.execute(total_query)
    total_sessions = total_result.scalar_one()

    # Completed sessions
    completed_query = select(func.count()).select_from(PomodoroSession).where(
        PomodoroSession.status == SessionStatus.COMPLETED
    )
    completed_result = await db.execute(completed_query)
    completed_sessions = completed_result.scalar_one()

    # Total work and break time
    work_query = select(func.sum(PomodoroSession.actual_duration)).where(
        and_(
            PomodoroSession.session_type == SessionType.WORK,
            PomodoroSession.actual_duration.isnot(None)
        )
    )
    work_result = await db.execute(work_query)
    total_work_time = work_result.scalar_one() or 0

    break_query = select(func.sum(PomodoroSession.actual_duration)).where(
        and_(
            PomodoroSession.session_type.in_([SessionType.SHORT_BREAK, SessionType.LONG_BREAK]),
            PomodoroSession.actual_duration.isnot(None)
        )
    )
    break_result = await db.execute(break_query)
    total_break_time = break_result.scalar_one() or 0

    # Average session duration
    avg_query = select(func.avg(PomodoroSession.actual_duration)).where(
        PomodoroSession.actual_duration.isnot(None)
    )
    avg_result = await db.execute(avg_query)
    average_duration = avg_result.scalar_one() or 0.0

    # Interruptions
    interruptions_query = select(func.sum(PomodoroSession.interruptions)).select_from(PomodoroSession)
    interruptions_result = await db.execute(interruptions_query)
    interruptions_count = interruptions_result.scalar_one() or 0

    # Today's sessions
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_query = select(func.count()).select_from(PomodoroSession).where(
        PomodoroSession.started_at >= today_start
    )
    today_result = await db.execute(today_query)
    today_sessions = today_result.scalar_one()

    # Today's work time
    today_work_query = select(func.sum(PomodoroSession.actual_duration)).where(
        and_(
            PomodoroSession.session_type == SessionType.WORK,
            PomodoroSession.started_at >= today_start,
            PomodoroSession.actual_duration.isnot(None)
        )
    )
    today_work_result = await db.execute(today_work_query)
    today_work_time = today_work_result.scalar_one() or 0

    # Current streak (consecutive days with at least one session)
    # Simplified: count sessions in last 7 days
    week_ago = datetime.utcnow() - timedelta(days=7)
    streak_query = select(func.count(func.distinct(func.date(PomodoroSession.started_at)))).where(
        PomodoroSession.started_at >= week_ago
    )
    streak_result = await db.execute(streak_query)
    current_streak = streak_result.scalar_one()

    return PomodoroStatsResponse(
        total_sessions=total_sessions,
        completed_sessions=completed_sessions,
        total_work_time=total_work_time,
        total_break_time=total_break_time,
        average_session_duration=average_duration,
        interruptions_count=interruptions_count,
        today_sessions=today_sessions,
        today_work_time=today_work_time,
        current_streak=current_streak,
    )
