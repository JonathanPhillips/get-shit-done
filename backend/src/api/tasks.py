"""Task management API endpoints."""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from src.core.database import get_db
from src.models.task import Task, TaskStatus
from src.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[TaskStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """
    List tasks with optional filtering.

    - **status**: Filter by task status
    - **skip**: Number of tasks to skip (pagination)
    - **limit**: Maximum number of tasks to return
    """
    query = select(Task)

    if status:
        query = query.where(Task.status == status)

    # Get total count
    count_query = select(func.count()).select_from(Task)
    if status:
        count_query = count_query.where(Task.status == status)
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Get tasks
    query = query.offset(skip).limit(limit).order_by(Task.created_at.desc())
    result = await db.execute(query)
    tasks = result.scalars().all()

    return TaskListResponse(tasks=tasks, total=total)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific task by ID."""
    query = select(Task).where(Task.id == task_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new task."""
    task = Task(**task_data.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing task."""
    query = select(Task).where(Task.id == task_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update fields
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    # Set completed_at if status changed to completed
    if task_data.status == TaskStatus.COMPLETED and not task.completed_at:
        task.completed_at = datetime.utcnow()
    elif task_data.status and task_data.status != TaskStatus.COMPLETED:
        task.completed_at = None

    task.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a task."""
    query = select(Task).where(Task.id == task_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.delete(task)
    await db.commit()
    return None


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Mark a task as completed."""
    query = select(Task).where(Task.id == task_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = TaskStatus.COMPLETED
    task.completed_at = datetime.utcnow()
    task.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(task)
    return task


@router.post("/{task_id}/increment-pomodoro", response_model=TaskResponse)
async def increment_pomodoro(
    task_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Increment the completed pomodoros count for a task."""
    query = select(Task).where(Task.id == task_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed_pomodoros += 1
    task.updated_at = datetime.utcnow()

    # Auto-complete if estimated pomodoros reached
    if task.completed_pomodoros >= task.estimated_pomodoros and task.status != TaskStatus.COMPLETED:
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(task)
    return task
