"""Tests for Pomodoro API endpoints."""
import pytest
from httpx import AsyncClient
from src.models.pomodoro import SessionType, SessionStatus


@pytest.mark.asyncio
async def test_start_work_session(client: AsyncClient):
    """Test starting a work session."""
    session_data = {
        "session_type": SessionType.WORK.value,
        "planned_duration": 1500,  # 25 minutes
        "session_number": 1,
    }

    response = await client.post("/api/pomodoro/sessions", json=session_data)
    assert response.status_code == 201

    data = response.json()
    assert data["session_type"] == SessionType.WORK.value
    assert data["status"] == SessionStatus.ACTIVE.value
    assert data["planned_duration"] == 1500
    assert data["session_number"] == 1
    assert "id" in data
    assert "started_at" in data


@pytest.mark.asyncio
async def test_start_break_session(client: AsyncClient):
    """Test starting a break session."""
    session_data = {
        "session_type": SessionType.SHORT_BREAK.value,
        "planned_duration": 300,  # 5 minutes
        "session_number": 1,
    }

    response = await client.post("/api/pomodoro/sessions", json=session_data)
    assert response.status_code == 201

    data = response.json()
    assert data["session_type"] == SessionType.SHORT_BREAK.value
    assert data["status"] == SessionStatus.ACTIVE.value


@pytest.mark.asyncio
async def test_start_session_with_task(client: AsyncClient):
    """Test starting a session linked to a task."""
    # Create a task first
    task_response = await client.post(
        "/api/tasks",
        json={"title": "Test Task", "priority": "medium"},
    )
    task_id = task_response.json()["id"]

    # Start session with task
    session_data = {
        "session_type": SessionType.WORK.value,
        "planned_duration": 1500,
        "task_id": task_id,
        "session_number": 1,
    }

    response = await client.post("/api/pomodoro/sessions", json=session_data)
    assert response.status_code == 201

    data = response.json()
    assert data["task_id"] == task_id


@pytest.mark.asyncio
async def test_get_active_session(client: AsyncClient):
    """Test getting the active session."""
    # No active session initially
    response = await client.get("/api/pomodoro/active")
    assert response.status_code == 200
    assert response.json() is None

    # Start a session
    await client.post(
        "/api/pomodoro/sessions",
        json={
            "session_type": SessionType.WORK.value,
            "planned_duration": 1500,
            "session_number": 1,
        },
    )

    # Get active session
    response = await client.get("/api/pomodoro/active")
    assert response.status_code == 200
    data = response.json()
    assert data is not None
    assert data["status"] == SessionStatus.ACTIVE.value


@pytest.mark.asyncio
async def test_auto_interrupt_on_new_session(client: AsyncClient):
    """Test that starting a new session interrupts the active one."""
    # Start first session
    response1 = await client.post(
        "/api/pomodoro/sessions",
        json={
            "session_type": SessionType.WORK.value,
            "planned_duration": 1500,
            "session_number": 1,
        },
    )
    session1_id = response1.json()["id"]

    # Start second session
    await client.post(
        "/api/pomodoro/sessions",
        json={
            "session_type": SessionType.SHORT_BREAK.value,
            "planned_duration": 300,
            "session_number": 2,
        },
    )

    # Check first session was interrupted
    response = await client.get(f"/api/pomodoro/sessions/{session1_id}")
    data = response.json()
    assert data["status"] == SessionStatus.INTERRUPTED.value
    assert data["ended_at"] is not None


@pytest.mark.asyncio
async def test_complete_session(client: AsyncClient):
    """Test completing a session."""
    # Start session
    start_response = await client.post(
        "/api/pomodoro/sessions",
        json={
            "session_type": SessionType.WORK.value,
            "planned_duration": 1500,
            "session_number": 1,
        },
    )
    session_id = start_response.json()["id"]

    # Complete session
    response = await client.post(f"/api/pomodoro/sessions/{session_id}/complete")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == SessionStatus.COMPLETED.value
    assert data["ended_at"] is not None
    assert data["actual_duration"] is not None


@pytest.mark.asyncio
async def test_interrupt_session(client: AsyncClient):
    """Test interrupting a session."""
    # Start session
    start_response = await client.post(
        "/api/pomodoro/sessions",
        json={
            "session_type": SessionType.WORK.value,
            "planned_duration": 1500,
            "session_number": 1,
        },
    )
    session_id = start_response.json()["id"]

    # Interrupt session
    response = await client.post(f"/api/pomodoro/sessions/{session_id}/interrupt")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == SessionStatus.INTERRUPTED.value
    assert data["ended_at"] is not None
    assert data["interruptions"] == 1


@pytest.mark.asyncio
async def test_list_sessions(client: AsyncClient):
    """Test listing sessions."""
    # Create multiple sessions
    for i in range(3):
        session_type = SessionType.WORK if i % 2 == 0 else SessionType.SHORT_BREAK
        await client.post(
            "/api/pomodoro/sessions",
            json={
                "session_type": session_type.value,
                "planned_duration": 1500 if session_type == SessionType.WORK else 300,
                "session_number": i + 1,
            },
        )

    response = await client.get("/api/pomodoro/sessions")
    assert response.status_code == 200

    data = response.json()
    assert len(data["sessions"]) == 3
    assert data["total"] == 3


@pytest.mark.asyncio
async def test_list_sessions_by_status(client: AsyncClient):
    """Test filtering sessions by status."""
    # Create and complete one session
    session1 = await client.post(
        "/api/pomodoro/sessions",
        json={
            "session_type": SessionType.WORK.value,
            "planned_duration": 1500,
            "session_number": 1,
        },
    )
    session1_id = session1.json()["id"]
    await client.post(f"/api/pomodoro/sessions/{session1_id}/complete")

    # Create an active session
    await client.post(
        "/api/pomodoro/sessions",
        json={
            "session_type": SessionType.WORK.value,
            "planned_duration": 1500,
            "session_number": 2,
        },
    )

    # Filter by completed
    response = await client.get(
        f"/api/pomodoro/sessions?status={SessionStatus.COMPLETED.value}"
    )
    data = response.json()
    assert len(data["sessions"]) == 1
    assert data["sessions"][0]["status"] == SessionStatus.COMPLETED.value

    # Filter by active (should be interrupted by the second session)
    response = await client.get(
        f"/api/pomodoro/sessions?status={SessionStatus.ACTIVE.value}"
    )
    data = response.json()
    assert len(data["sessions"]) == 1


@pytest.mark.asyncio
async def test_pomodoro_stats_empty(client: AsyncClient):
    """Test stats when no sessions exist."""
    response = await client.get("/api/pomodoro/stats")
    assert response.status_code == 200

    data = response.json()
    assert data["total_sessions"] == 0
    assert data["completed_sessions"] == 0
    assert data["total_work_time"] == 0
    assert data["total_break_time"] == 0


@pytest.mark.asyncio
async def test_pomodoro_stats_with_sessions(client: AsyncClient):
    """Test stats with completed sessions."""
    # Create and complete work sessions
    for i in range(2):
        session = await client.post(
            "/api/pomodoro/sessions",
            json={
                "session_type": SessionType.WORK.value,
                "planned_duration": 1500,
                "session_number": i + 1,
            },
        )
        session_id = session.json()["id"]
        await client.post(f"/api/pomodoro/sessions/{session_id}/complete")

    # Create and complete a break session
    break_session = await client.post(
        "/api/pomodoro/sessions",
        json={
            "session_type": SessionType.SHORT_BREAK.value,
            "planned_duration": 300,
            "session_number": 3,
        },
    )
    break_id = break_session.json()["id"]
    await client.post(f"/api/pomodoro/sessions/{break_id}/complete")

    # Get stats
    response = await client.get("/api/pomodoro/stats")
    assert response.status_code == 200

    data = response.json()
    assert data["total_sessions"] == 3
    assert data["completed_sessions"] == 3
    assert data["total_work_time"] > 0
    assert data["total_break_time"] > 0
    assert data["today_sessions"] == 3


@pytest.mark.asyncio
async def test_session_pagination(client: AsyncClient):
    """Test session list pagination."""
    # Create 10 sessions
    for i in range(10):
        await client.post(
            "/api/pomodoro/sessions",
            json={
                "session_type": SessionType.WORK.value,
                "planned_duration": 1500,
                "session_number": i + 1,
            },
        )

    # Get first page
    response = await client.get("/api/pomodoro/sessions?skip=0&limit=5")
    data = response.json()
    assert len(data["sessions"]) == 5
    assert data["total"] == 10

    # Get second page
    response = await client.get("/api/pomodoro/sessions?skip=5&limit=5")
    data = response.json()
    assert len(data["sessions"]) == 5
