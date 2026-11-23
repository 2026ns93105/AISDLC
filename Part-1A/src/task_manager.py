"""Task management operations and command-line interface."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

TASKS_FILE = Path(__file__).resolve().parent.parent / "tasks.json"
PRIORITIES = ("High", "Medium", "Low")
STATUSES = ("Pending", "In Progress", "Completed")
PRIORITY_ORDER = {priority: index for index, priority in enumerate(PRIORITIES)}
TASK_FIELDS = {"id", "title", "description", "priority", "status", "tags"}
UPDATABLE_FIELDS = {"title", "description", "priority", "status", "tags"}


def _validate_task(task: Any) -> dict[str, Any]:
    """Validate a task object and return a normalized copy."""
    if not isinstance(task, dict):
        raise TypeError("Each task must be a JSON object.")
    if set(task) != TASK_FIELDS:
        missing = sorted(TASK_FIELDS - set(task))
        extra = sorted(set(task) - TASK_FIELDS)
        details = []
        if missing:
            details.append(f"missing fields: {', '.join(missing)}")
        if extra:
            details.append(f"unexpected fields: {', '.join(extra)}")
        raise ValueError(f"Invalid task fields ({'; '.join(details)}).")

    task_id = task["id"]
    if isinstance(task_id, bool) or not isinstance(task_id, int) or task_id < 1:
        raise ValueError("Task id must be a positive integer.")
    title = task["title"]
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Task title must be a non-empty string.")
    description = task["description"]
    if not isinstance(description, str):
        raise TypeError("Task description must be a string.")
    priority = task["priority"]
    if priority not in PRIORITIES:
        raise ValueError(f"Priority must be one of: {', '.join(PRIORITIES)}.")
    status = task["status"]
    if status not in STATUSES:
        raise ValueError(f"Status must be one of: {', '.join(STATUSES)}.")
    tags = task["tags"]
    if not isinstance(tags, list) or any(
        not isinstance(tag, str) or not tag.strip() for tag in tags
    ):
        raise ValueError("Tags must be a list of non-empty strings.")

    return {
        "id": task_id,
        "title": title.strip(),
        "description": description,
        "priority": priority,
        "status": status,
        "tags": [tag.strip() for tag in tags],
    }


def load_tasks(path: str | Path | None = None) -> list[dict[str, Any]]:
    """Load and validate tasks from JSON, returning an empty list if absent."""
    file_path = Path(path) if path is not None else TASKS_FILE
    try:
        with file_path.open("r", encoding="utf-8") as tasks_file:
            tasks = json.load(tasks_file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as error:
        raise ValueError(f"Task file contains invalid JSON: {file_path}") from error

    if not isinstance(tasks, list):
        raise TypeError("Task file must contain a JSON array.")
    validated = [_validate_task(task) for task in tasks]
    ids = [task["id"] for task in validated]
    if len(ids) != len(set(ids)):
        raise ValueError("Task file contains duplicate task IDs.")
    return validated


def save_tasks(
    tasks: list[dict[str, Any]], path: str | Path | None = None
) -> None:
    """Validate and atomically save all tasks as formatted JSON."""
    if not isinstance(tasks, list):
        raise TypeError("Tasks must be provided as a list.")
    validated = [_validate_task(task) for task in tasks]
    ids = [task["id"] for task in validated]
    if len(ids) != len(set(ids)):
        raise ValueError("Task IDs must be unique.")

    file_path = Path(path) if path is not None else TASKS_FILE
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=file_path.parent,
            prefix=f".{file_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = temporary_file.name
            json.dump(validated, temporary_file, indent=2, ensure_ascii=False)
            temporary_file.write("\n")
        os.replace(temporary_path, file_path)
    except OSError:
        if temporary_path is not None:
            try:
                os.unlink(temporary_path)
            except FileNotFoundError:
                pass
        raise


def add_task(
    task_id: int,
    title: str,
    description: str = "",
    priority: str = "Medium",
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Create, persist, and return a task with the given attributes."""
    task = _validate_task(
        {
            "id": task_id,
            "title": title,
            "description": description,
            "priority": priority,
            "status": "Pending",
            "tags": [] if tags is None else tags,
        }
    )
    tasks = load_tasks()
    if any(existing["id"] == task["id"] for existing in tasks):
        raise ValueError(f"Task ID {task['id']} already exists.")
    tasks.append(task)
    save_tasks(tasks)
    return task.copy()


def get_tasks() -> list[dict[str, Any]]:
    """Return all persisted tasks in their stored order."""
    return load_tasks()


def update_task(task_id: int, **updates: Any) -> dict[str, Any]:
    """Update permitted task fields, persist the change, and return the task."""
    if isinstance(task_id, bool) or not isinstance(task_id, int) or task_id < 1:
        raise ValueError("Task id must be a positive integer.")
    unsupported = set(updates) - UPDATABLE_FIELDS
    if unsupported:
        raise ValueError(f"Fields cannot be updated: {', '.join(sorted(unsupported))}.")
    if not updates:
        raise ValueError("At least one task field must be provided for update.")

    tasks = load_tasks()
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            updated_task = _validate_task({**task, **updates})
            tasks[index] = updated_task
            save_tasks(tasks)
            return updated_task.copy()
    raise KeyError(f"Task ID {task_id} was not found.")


def delete_task(task_id: int) -> bool:
    """Delete a task by ID, persist the change, and report whether it existed."""
    if isinstance(task_id, bool) or not isinstance(task_id, int) or task_id < 1:
        raise ValueError("Task id must be a positive integer.")
    tasks = load_tasks()
    remaining = [task for task in tasks if task["id"] != task_id]
    if len(remaining) == len(tasks):
        return False
    save_tasks(remaining)
    return True


def filter_by_tag(tag: str) -> list[dict[str, Any]]:
    """Return tasks that contain the requested tag, ignoring tag case."""
    if not isinstance(tag, str) or not tag.strip():
        raise ValueError("Tag must be a non-empty string.")
    normalized_tag = tag.strip().casefold()
    return [
        task
        for task in load_tasks()
        if any(existing.casefold() == normalized_tag for existing in task["tags"])
    ]


def sort_by_priority() -> list[dict[str, Any]]:
    """Return tasks sorted by priority from High to Low."""
    return sorted(
        load_tasks(),
        key=lambda task: (PRIORITY_ORDER[task["priority"]], task["id"]),
    )


def update_status(task_id: int, status: str) -> dict[str, Any]:
    """Set a task's status and persist the updated task."""
    return update_task(task_id, status=status)


def _build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(description="Manage tasks stored in tasks.json.")
    commands = parser.add_subparsers(dest="command", required=True)

    add_parser = commands.add_parser("add", help="Create a task.")
    add_parser.add_argument("id", type=int)
    add_parser.add_argument("title")
    add_parser.add_argument("--description", default="")
    add_parser.add_argument("--priority", choices=PRIORITIES, default="Medium")
    add_parser.add_argument("--tag", action="append", default=[])

    commands.add_parser("list", help="View all tasks.")
    filter_parser = commands.add_parser("filter", help="Filter tasks by tag.")
    filter_parser.add_argument("tag")
    commands.add_parser("sort", help="View tasks sorted by priority.")

    update_parser = commands.add_parser("update", help="Update task fields.")
    update_parser.add_argument("id", type=int)
    update_parser.add_argument("--title")
    update_parser.add_argument("--description")
    update_parser.add_argument("--priority", choices=PRIORITIES)
    update_parser.add_argument("--tag", action="append")

    delete_parser = commands.add_parser("delete", help="Delete a task.")
    delete_parser.add_argument("id", type=int)
    status_parser = commands.add_parser("status", help="Update task status.")
    status_parser.add_argument("id", type=int)
    status_parser.add_argument("status", choices=STATUSES)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the command-line interface and return an exit status."""
    parser = _build_parser()
    arguments = parser.parse_args(argv)
    try:
        if arguments.command == "add":
            result: Any = add_task(
                arguments.id,
                arguments.title,
                arguments.description,
                arguments.priority,
                arguments.tag,
            )
        elif arguments.command == "list":
            result = get_tasks()
        elif arguments.command == "filter":
            result = filter_by_tag(arguments.tag)
        elif arguments.command == "sort":
            result = sort_by_priority()
        elif arguments.command == "update":
            updates = {
                "title": arguments.title,
                "description": arguments.description,
                "priority": arguments.priority,
                "tags": arguments.tag,
            }
            result = update_task(
                arguments.id,
                **{key: value for key, value in updates.items() if value is not None},
            )
        elif arguments.command == "delete":
            if not delete_task(arguments.id):
                raise KeyError(f"Task ID {arguments.id} was not found.")
            result = {"deleted": arguments.id}
        else:
            result = update_status(arguments.id, arguments.status)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (KeyError, OSError, TypeError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
