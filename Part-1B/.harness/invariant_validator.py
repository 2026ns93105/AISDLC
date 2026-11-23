"""Layer 2: business rules that must hold for every response."""

from datetime import datetime


SUPPORTED_INTENTS = {
    "create_reminder",
    "reschedule_reminder",
    "snooze_reminder",
    "clarification_required",
}


def validate_invariants(response):
    errors = []
    if not isinstance(response, dict):
        return False, ["response must be an object"]
    intent = response.get("intent")
    task = response.get("task")
    reminder_datetime = response.get("datetime")
    if intent not in SUPPORTED_INTENTS:
        errors.append("unsupported intent")
    if intent == "clarification_required":
        if response.get("status") != "needs_clarification":
            errors.append("clarification must use needs_clarification status")
        if not isinstance(response.get("reason"), str) or not response["reason"].strip():
            errors.append("clarification must include a reason")
        if reminder_datetime is not None:
            errors.append("clarification must not claim a scheduled datetime")
    else:
        if not isinstance(task, str) or not task.strip():
            errors.append("scheduled reminder must have a task")
        if response.get("status") != "scheduled":
            errors.append("successful intent must use scheduled status")
        if response.get("reason") is not None:
            errors.append("successful response reason must be null")
        if not isinstance(reminder_datetime, str):
            errors.append("scheduled reminder must have a datetime")
        else:
            try:
                datetime.fromisoformat(reminder_datetime)
            except ValueError:
                errors.append("scheduled datetime is invalid")
    return not errors, errors
