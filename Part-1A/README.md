# Smart Todo Manager

A Python 3 task manager with validated JSON persistence, a reusable Python API,
and a command-line interface.

## Requirements

- Python 3.10 or later
- Packages listed in `requirements.txt` for development checks

Install the development tools with:

```sh
python -m pip install -r requirements.txt
```

## Run

Run commands from the project root. Examples:

```sh
python -m src.task_manager add 1 "Prepare report" --priority High --tag work
python -m src.task_manager list
python -m src.task_manager filter work
python -m src.task_manager sort
python -m src.task_manager update 1 --title "Finish report" --tag urgent
python -m src.task_manager status 1 "In Progress"
python -m src.task_manager delete 1
```

Use `python -m src.task_manager --help` or append `--help` to a subcommand for
complete command usage. Successful commands print JSON. Task data is stored in
the project-root `tasks.json`.

## Python API

```python
from src.task_manager import add_task, filter_by_tag, get_tasks, update_status

add_task(1, "Prepare report", priority="High", tags=["work"])
print(get_tasks())
print(filter_by_tag("work"))
update_status(1, "In Progress")
```

The module also provides `load_tasks`, `save_tasks`, `update_task`,
`delete_task`, and `sort_by_priority`. See
[`specs/specification.md`](specs/specification.md) for field constraints and
error behavior.

## Validation

Run all quality checks on Windows:

```bat
.harness\run_harness.bat
```

On Linux or macOS:

```sh
sh .harness/run_harness.sh
```

The harness checks Ruff formatting/lint rules, Bandit security findings, and
the pytest suite.
