"""Tests for task API endpoints."""
import pytest
from httpx import AsyncClient
from src.models.task import TaskStatus, TaskPriority


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient):
    """Test creating a new task."""
    task_data = {
        "title": "Test Task",
        "description": "Test description",
        "priority": TaskPriority.HIGH.value,
        "estimated_pomodoros": 3,
    }

    response = await client.post("/api/tasks", json=task_data)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]
    assert data["priority"] == task_data["priority"]
    assert data["estimated_pomodoros"] == task_data["estimated_pomodoros"]
    assert data["status"] == TaskStatus.TODO.value
    assert data["completed_pomodoros"] == 0
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_list_tasks_empty(client: AsyncClient):
    """Test listing tasks when none exist."""
    response = await client.get("/api/tasks")
    assert response.status_code == 200

    data = response.json()
    assert data["tasks"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_tasks(client: AsyncClient):
    """Test listing tasks."""
    # Create multiple tasks
    for i in range(3):
        await client.post(
            "/api/tasks",
            json={
                "title": f"Task {i}",
                "priority": TaskPriority.MEDIUM.value,
            },
        )

    response = await client.get("/api/tasks")
    assert response.status_code == 200

    data = response.json()
    assert len(data["tasks"]) == 3
    assert data["total"] == 3


@pytest.mark.asyncio
async def test_list_tasks_with_status_filter(client: AsyncClient):
    """Test filtering tasks by status."""
    # Create tasks with different statuses
    task1 = await client.post(
        "/api/tasks",
        json={"title": "Todo Task", "priority": TaskPriority.MEDIUM.value},
    )
    task1_id = task1.json()["id"]

    await client.post(
        "/api/tasks",
        json={"title": "Another Todo", "priority": TaskPriority.LOW.value},
    )

    # Complete one task
    await client.post(f"/api/tasks/{task1_id}/complete")

    # Filter by TODO status
    response = await client.get(f"/api/tasks?status={TaskStatus.TODO.value}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["title"] == "Another Todo"

    # Filter by COMPLETED status
    response = await client.get(f"/api/tasks?status={TaskStatus.COMPLETED.value}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["title"] == "Todo Task"


@pytest.mark.asyncio
async def test_get_task(client: AsyncClient):
    """Test getting a specific task."""
    # Create task
    create_response = await client.post(
        "/api/tasks",
        json={"title": "Get Task Test", "priority": TaskPriority.URGENT.value},
    )
    task_id = create_response.json()["id"]

    # Get task
    response = await client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Get Task Test"


@pytest.mark.asyncio
async def test_get_task_not_found(client: AsyncClient):
    """Test getting a non-existent task."""
    response = await client.get("/api/tasks/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_task(client: AsyncClient):
    """Test updating a task."""
    # Create task
    create_response = await client.post(
        "/api/tasks",
        json={"title": "Original Title", "priority": TaskPriority.LOW.value},
    )
    task_id = create_response.json()["id"]

    # Update task
    update_data = {
        "title": "Updated Title",
        "priority": TaskPriority.HIGH.value,
        "status": TaskStatus.IN_PROGRESS.value,
    }
    response = await client.patch(f"/api/tasks/{task_id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["priority"] == TaskPriority.HIGH.value
    assert data["status"] == TaskStatus.IN_PROGRESS.value


@pytest.mark.asyncio
async def test_delete_task(client: AsyncClient):
    """Test deleting a task."""
    # Create task
    create_response = await client.post(
        "/api/tasks",
        json={"title": "Delete Me", "priority": TaskPriority.MEDIUM.value},
    )
    task_id = create_response.json()["id"]

    # Delete task
    response = await client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 204

    # Verify task is deleted
    get_response = await client.get(f"/api/tasks/{task_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_complete_task(client: AsyncClient):
    """Test marking a task as completed."""
    # Create task
    create_response = await client.post(
        "/api/tasks",
        json={"title": "Complete Me", "priority": TaskPriority.MEDIUM.value},
    )
    task_id = create_response.json()["id"]

    # Complete task
    response = await client.post(f"/api/tasks/{task_id}/complete")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == TaskStatus.COMPLETED.value
    assert data["completed_at"] is not None


@pytest.mark.asyncio
async def test_increment_pomodoro(client: AsyncClient):
    """Test incrementing pomodoro count."""
    # Create task
    create_response = await client.post(
        "/api/tasks",
        json={
            "title": "Pomodoro Task",
            "priority": TaskPriority.MEDIUM.value,
            "estimated_pomodoros": 3,
        },
    )
    task_id = create_response.json()["id"]

    # Increment pomodoro
    response = await client.post(f"/api/tasks/{task_id}/increment-pomodoro")
    assert response.status_code == 200

    data = response.json()
    assert data["completed_pomodoros"] == 1

    # Increment again
    response = await client.post(f"/api/tasks/{task_id}/increment-pomodoro")
    assert response.status_code == 200
    data = response.json()
    assert data["completed_pomodoros"] == 2


@pytest.mark.asyncio
async def test_auto_complete_on_pomodoro_goal(client: AsyncClient):
    """Test task auto-completes when pomodoro goal is reached."""
    # Create task with 2 estimated pomodoros
    create_response = await client.post(
        "/api/tasks",
        json={
            "title": "Auto Complete Task",
            "priority": TaskPriority.MEDIUM.value,
            "estimated_pomodoros": 2,
        },
    )
    task_id = create_response.json()["id"]

    # Increment to goal
    await client.post(f"/api/tasks/{task_id}/increment-pomodoro")
    response = await client.post(f"/api/tasks/{task_id}/increment-pomodoro")

    data = response.json()
    assert data["completed_pomodoros"] == 2
    assert data["status"] == TaskStatus.COMPLETED.value
    assert data["completed_at"] is not None


@pytest.mark.asyncio
async def test_pagination(client: AsyncClient):
    """Test task list pagination."""
    # Create 10 tasks
    for i in range(10):
        await client.post(
            "/api/tasks",
            json={"title": f"Task {i}", "priority": TaskPriority.MEDIUM.value},
        )

    # Get first page
    response = await client.get("/api/tasks?skip=0&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["tasks"]) == 5
    assert data["total"] == 10

    # Get second page
    response = await client.get("/api/tasks?skip=5&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["tasks"]) == 5
    assert data["total"] == 10
