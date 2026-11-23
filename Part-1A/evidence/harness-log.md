# Harness Run Evidence

The project harness runs these checks from the project root:

```text
ruff check .
bandit -r src
pytest
```

## Results

Verified on Windows with Python 3.14.6:

- `ruff check .` — passed.
- `bandit -r src` — passed; no issues identified.
- `pytest` — passed; 9 tests passed.
- `python -m src.task_manager --help` — passed; all seven commands are listed.

The task store remains a valid empty JSON array (`[]`) after validation.
