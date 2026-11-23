# Smart Todo Manager Specification

## Overview

Smart Todo Manager is a Python 3 application that manages tasks in `tasks.json`.
It provides reusable task operations and a command-line interface.

## Task Schema

Each task is a JSON object with exactly these fields:

| Field | Type | Constraints |
| --- | --- | --- |
| `id` | integer | Positive and unique; booleans are not accepted as integers |
| `title` | string | Non-empty after trimming whitespace |
| `description` | string | May be empty |
| `priority` | string | `High`, `Medium`, or `Low` |
| `status` | string | `Pending`, `In Progress`, or `Completed` |
| `tags` | list of strings | Each tag must be non-empty after trimming |

New tasks default to `Medium` priority, `Pending` status, an empty description,
and no tags. Tag matching is case-insensitive.

## Functional Requirements

1. Create a task with a unique ID.
2. View all tasks in stored order.
3. Update a task's title, description, priority, status, or tags.
4. Delete a task so it no longer appears in output.
5. Filter tasks by tag.
6. Sort tasks by priority in `High`, `Medium`, `Low` order.
7. Update a task's status.
8. Load from and save to JSON persistence.
9. Reject malformed task data and report storage or validation failures.

## Reusable Python API

`src.task_manager` exposes `load_tasks()`, `save_tasks(tasks)`, `add_task(...)`,
`get_tasks()`, `update_task(task_id, **updates)`, `delete_task(task_id)`,
`filter_by_tag(tag)`, `sort_by_priority()`, and
`update_status(task_id, status)`. Load and save accept an optional path for
testing or alternate stores; otherwise the project-root `tasks.json` is used.
`add_task` accepts `task_id`, `title`, and optional `description`, `priority`,
and `tags`. Missing update IDs raise `KeyError`; deleting a missing ID returns
`False`.

## Command-Line Interface

Run `python -m src.task_manager --help` for the available commands: `add`,
`list`, `update`, `delete`, `filter`, `sort`, and `status`. Successful commands
print JSON; invalid operations print an error and return a non-zero exit status.

## Acceptance Criteria

### AC1

Task must be stored in tasks.json.

### AC2

Tasks can be filtered by tag.

### AC3

Priority order:
High > Medium > Low

### AC4

Status updates must persist.

### AC5

Deleted tasks shall not appear in output.

## Quality Requirements

The implementation must be Python 3, PEP 8 compliant, and pass Ruff, Bandit,
and the complete pytest suite through the supplied harness scripts.
