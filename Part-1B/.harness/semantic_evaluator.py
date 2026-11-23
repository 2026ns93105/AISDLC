"""Layer 3: expected meaning and task extraction checks for dataset cases."""

from datetime import datetime


def evaluate_semantics(case, response):
    errors = []
    expected_intent = case["expected_intent"]
    if response.get("intent") != expected_intent:
        errors.append(f"expected intent {expected_intent!r}, got {response.get('intent')!r}")

    prop = case["expected_property"]
    task = str(response.get("task", "")).casefold()
    if prop == "datetime_present":
        if not isinstance(response.get("datetime"), str):
            errors.append("expected a resolved datetime")
    elif prop == "datetime_null":
        if response.get("datetime") is not None:
            errors.append("expected datetime to be null")
    elif prop == "task_empty":
        if task.strip():
            errors.append("expected an empty task")
    elif prop == "clarification":
        if response.get("intent") != "clarification_required":
            errors.append("expected clarification behavior")
    elif prop.startswith("task_contains:"):
        expected_text = prop.split(":", 1)[1].casefold()
        if expected_text not in task:
            errors.append(f"task does not contain {expected_text!r}")
    elif prop == "valid_datetime":
        value = response.get("datetime")
        try:
            datetime.fromisoformat(value)
        except (TypeError, ValueError):
            errors.append("expected a valid ISO datetime")
    else:
        errors.append(f"unknown expected_property {prop!r}")
    return not errors, errors
