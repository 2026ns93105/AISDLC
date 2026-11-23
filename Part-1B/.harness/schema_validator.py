"""Layer 1: response shape and JSON datatype checks."""

import json
from datetime import datetime


REQUIRED_FIELDS = {"intent", "task", "datetime", "status", "reason"}
ALLOWED_INTENTS = {
    "create_reminder",
    "reschedule_reminder",
    "snooze_reminder",
    "clarification_required",
}


def validate_schema(response):
    errors = []
    if isinstance(response, str):
        try:
            response = json.loads(response)
        except json.JSONDecodeError as exc:
            return False, [f"invalid JSON: {exc.msg}"]
    if not isinstance(response, dict):
        return False, ["response must be a JSON object"]
    missing = REQUIRED_FIELDS - set(response)
    extra = set(response) - REQUIRED_FIELDS
    if missing:
        errors.append("missing fields: " + ", ".join(sorted(missing)))
    if extra:
        errors.append("unexpected fields: " + ", ".join(sorted(extra)))
    for field in ("intent", "task", "status"):
        if field in response and not isinstance(response[field], str):
            errors.append(f"{field} must be a string")
    if "datetime" in response:
        value = response["datetime"]
        if value is not None and not isinstance(value, str):
            errors.append("datetime must be a string or null")
        elif isinstance(value, str):
            try:
                datetime.fromisoformat(value)
            except ValueError:
                errors.append("datetime must be a valid ISO 8601 datetime")
    if "reason" in response and response["reason"] is not None and not isinstance(response["reason"], str):
        errors.append("reason must be a string or null")
    if "intent" in response and isinstance(response["intent"], str) and response["intent"] not in ALLOWED_INTENTS:
        errors.append("intent is not supported")
    return not errors, errors
