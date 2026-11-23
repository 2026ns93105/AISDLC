# Natural Language Reminder Agent

A deterministic, local Python agent that converts free-text reminder requests into structured JSON. It supports creating, rescheduling, and snoozing reminders, and asks for clarification rather than guessing when a task or complete date/time is missing.

## Requirements
- Python 3.9 or newer
- `pytest` for tests (`python -m pip install -r requirements.txt`)

The parser and evaluation harness otherwise use only the Python standard library.

## Run the agent

Pass a request as command-line arguments:

```powershell
python src\agent.py Remind me to call Alex tomorrow at 3pm
```

Or pipe a request through standard input:

```powershell
'Remind me to call Alex tomorrow at 3pm' | python src\agent.py
```

The CLI prints a single JSON object. The Python API is `process_request(text, now=None)` from `src/agent.py`; the optional `now` parameter provides a deterministic reference time for relative expressions.

Supported date expressions include ISO dates, common numeric dates, month-name dates, today/tomorrow, weekdays, explicit 12/24-hour clock times, `in N hours/days`, and snooze durations such as `for 10 minutes`. Requests with date only, time only, vague timing, invalid values, missing task, or unsupported actions return `clarification_required`.

## Test and evaluate

```powershell
python -m pytest -q
python .harness\evaluation_runner.py
```

The evaluation runner checks every dataset case with schema, invariant, and semantic validators, reports the aggregate percentage score (80% pass threshold), and saves detailed results to `evidence\eval-results.json`.

## Project layout

- `specs\`: product contract, assumptions, plan, acceptance criteria, and tasks
- `src\`: agent API/CLI and deterministic natural-language parser
- `prompts\`: behavioral contract for an AI implementation
- `tests\`: pytest unit tests
- `evals\`: evaluation dataset
- `.harness\`: three evaluation layers and runner
- `evidence\`: evaluation results and harness methodology
