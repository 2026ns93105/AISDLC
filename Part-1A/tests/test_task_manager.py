"""Tests for Smart Todo Manager operations and JSON persistence."""

import json

import pytest

from src import task_manager


@pytest.fixture
def task_file(tmp_path, monkeypatch):
    """Use a temporary JSON file for each test."""
    path = tmp_path / "tasks.json"
    monkeypatch.setattr(task_manager, "TASKS_FILE", path)
    return path


def test_create_task(task_file):
    """A new task has defaults and is persisted."""
    created = task_manager.add_task(1, "Write tests", tags=["work"])

    assert created == {
        "id": 1,
        "title": "Write tests",
        "description": "",
        "priority": "Medium",
        "status": "Pending",
        "tags": ["work"],
    }
    assert task_manager.get_tasks() == [created]


def test_duplicate_task_id_is_rejected(task_file):
    """A duplicate ID is rejected without modifying stored tasks."""
    task_manager.add_task(1, "First")

    with pytest.raises(ValueError, match="already exists"):
        task_manager.add_task(1, "Second")

    assert [task["title"] for task in task_manager.get_tasks()] == ["First"]


def test_update_task(task_file):
    """Task fields can be updated and the updated object is returned."""
    task_manager.add_task(2, "Old title")

    updated = task_manager.update_task(
        2, title="New title", description="Details", priority="High"
    )

    assert updated["title"] == "New title"
    assert updated["description"] == "Details"
    assert updated["priority"] == "High"
    assert task_manager.get_tasks()[0] == updated


def test_delete_task(task_file):
    """Deleting a task removes it from output and persisted data."""
    task_manager.add_task(3, "Remove me")

    assert task_manager.delete_task(3) is True
    assert task_manager.delete_task(3) is False
    assert task_manager.get_tasks() == []


def test_filter_by_tag_is_case_insensitive(task_file):
    """Filtering matches tags without regard to letter case."""
    task_manager.add_task(1, "Tagged", tags=["Work"])
    task_manager.add_task(2, "Other", tags=["home"])

    assert [task["id"] for task in task_manager.filter_by_tag("work")] == [1]


def test_sort_by_priority(task_file):
    """Tasks are ordered High, Medium, Low with stable ID tie breaking."""
    task_manager.add_task(1, "Low task", priority="Low")
    task_manager.add_task(2, "Medium task")
    task_manager.add_task(3, "High task", priority="High")

    assert [
        task["priority"] for task in task_manager.sort_by_priority()
    ] == ["High", "Medium", "Low"]


def test_status_update_persists(task_file):
    """A status change is reflected in the JSON file."""
    task_manager.add_task(4, "Finish assignment")

    task_manager.update_status(4, "In Progress")

    stored = json.loads(task_file.read_text(encoding="utf-8"))
    assert stored[0]["status"] == "In Progress"


def test_load_tasks_validates_persisted_json(task_file):
    """Persisted JSON is loaded, while malformed JSON is reported clearly."""
    task_manager.save_tasks(
        [
            {
                "id": 5,
                "title": "Persisted task",
                "description": "",
                "priority": "Low",
                "status": "Completed",
                "tags": [],
            }
        ]
    )
    assert task_manager.load_tasks() == task_manager.get_tasks()

    task_file.write_text("{invalid", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid JSON"):
        task_manager.load_tasks()


def test_invalid_task_values_are_rejected(task_file):
    """Invalid values cannot enter the task store."""
    with pytest.raises(ValueError, match="Priority"):
        task_manager.add_task(1, "Invalid priority", priority="Urgent")
