"""Deterministic extraction of reminder intent, task, and date/time."""

from __future__ import annotations

import re
from datetime import datetime, time, timedelta
from typing import Optional, Tuple


_MONTHS = (
    "january|february|march|april|may|june|july|august|"
    "september|october|november|december"
)
_DATE_PATTERNS = (
    re.compile(r"\b\d{4}-\d{1,2}-\d{1,2}\b", re.IGNORECASE),
    re.compile(rf"\b(?:{_MONTHS})\s+\d{{1,2}}(?:,?\s+\d{{4}})?\b", re.IGNORECASE),
    re.compile(rf"\b\d{{1,2}}\s+(?:{_MONTHS})(?:\s+\d{{4}})?\b", re.IGNORECASE),
    re.compile(r"\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b"),
    re.compile(r"\b(?:day after tomorrow|today|tomorrow)\b", re.IGNORECASE),
    re.compile(
        r"\b(?:(?:next|this)\s+)?(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
        re.IGNORECASE,
    ),
)
_TIME_PATTERN = re.compile(
    r"\b(?:[01]?\d|2[0-3]):[0-5]\d(?:\s*[ap]\.?m\.?)?"
    r"|\b(?:1[0-2]|0?[1-9])(?::[0-5]\d)?\s*[ap]\.?m\.?"
    r"|\b(?:noon|midnight)\b",
    re.IGNORECASE,
)
_INVALID_TIME_PATTERN = re.compile(r"\b\d{1,2}:\d{2}\b")
_RELATIVE_PATTERN = re.compile(r"\bin\s+(\d+)\s+(minutes?|hours?|days?|weeks?)\b", re.IGNORECASE)
_SNOOZE_DURATION = re.compile(r"\bfor\s+(\d+)\s+(minutes?|hours?|days?|weeks?)\b", re.IGNORECASE)
_UNSPECIFIC_DATE = re.compile(
    r"\b(?:later|soon|sometime|next week|this week|next month|this afternoon|"
    r"this evening|tonight)\b",
    re.IGNORECASE,
)
_UNSUPPORTED_ACTION = re.compile(r"\b(?:delete|remove|cancel)\b", re.IGNORECASE)
_SNOOZE_ACTION = re.compile(r"\b(?:snooze|postpone)\b", re.IGNORECASE)
_RESCHEDULE_ACTION = re.compile(r"\b(?:reschedule|move|change|push back)\b", re.IGNORECASE)


def _intent(text: str) -> Tuple[str, bool]:
    if _UNSUPPORTED_ACTION.search(text):
        return "clarification_required", True
    if _SNOOZE_ACTION.search(text):
        return "snooze_reminder", False
    if _RESCHEDULE_ACTION.search(text):
        return "reschedule_reminder", False
    return "create_reminder", False


def _parse_calendar_date(value: str, now: datetime) -> Optional[datetime]:
    lowered = value.lower().strip()
    if lowered == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    if lowered == "tomorrow":
        return (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    if lowered == "day after tomorrow":
        return (now + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)

    weekday_match = re.fullmatch(
        r"(?:(next|this)\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
        lowered,
    )
    if weekday_match:
        names = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
        target = names.index(weekday_match.group(2))
        delta = (target - now.weekday()) % 7
        if weekday_match.group(1) == "next" and delta == 0:
            delta = 7
        return (now + timedelta(days=delta)).replace(hour=0, minute=0, second=0, microsecond=0)

    formats = (
        ("%Y-%m-%d", value),
        ("%B %d, %Y", value.title()),
        ("%B %d %Y", value.title()),
        ("%d %B %Y", value.title()),
        ("%m/%d/%Y", value),
        ("%m/%d/%y", value),
        ("%m-%d-%Y", value),
        ("%m-%d-%y", value),
    )
    for fmt, candidate in formats:
        try:
            parsed = datetime.strptime(candidate, fmt)
            return parsed.replace(hour=0, minute=0, second=0, microsecond=0)
        except ValueError:
            continue

    yearless_formats = (
        ("%B %d %Y", lambda year: f"{value.title()} {year}"),
        ("%d %B %Y", lambda year: f"{value.title()} {year}"),
        ("%m/%d/%Y", lambda year: f"{value}/{year}"),
        ("%m-%d-%Y", lambda year: f"{value}-{year}"),
    )
    for year in range(now.year, now.year + 9):
        for fmt, candidate_for_year in yearless_formats:
            try:
                parsed = datetime.strptime(candidate_for_year(year), fmt)
            except ValueError:
                continue
            if parsed.date() >= now.date():
                return parsed.replace(hour=0, minute=0, second=0, microsecond=0)
    return None


def _parse_clock(value: str) -> Optional[time]:
    lowered = re.sub(r"\s+", "", value.lower()).replace(".", "")
    if lowered == "noon":
        return time(12, 0)
    if lowered == "midnight":
        return time(0, 0)
    match = re.fullmatch(r"(\d{1,2})(?::(\d{2}))?([ap]m)?", lowered)
    if not match:
        return None
    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    suffix = match.group(3)
    if suffix:
        if not 1 <= hour <= 12:
            return None
        hour = hour % 12 + (12 if suffix == "pm" else 0)
    elif not 0 <= hour <= 23:
        return None
    return time(hour, minute)


def _as_duration(amount: int, unit: str) -> timedelta:
    unit = unit.lower().rstrip("s")
    if unit == "minute":
        return timedelta(minutes=amount)
    if unit == "hour":
        return timedelta(hours=amount)
    if unit == "day":
        return timedelta(days=amount)
    return timedelta(weeks=amount)


def _extract_datetime(text: str, now: datetime) -> Tuple[Optional[datetime], Optional[str], list[Tuple[int, int]]]:
    duration_match = _SNOOZE_DURATION.search(text)
    if duration_match and _SNOOZE_ACTION.search(text):
        amount = int(duration_match.group(1))
        if amount > 0:
            return now + _as_duration(amount, duration_match.group(2)), None, [duration_match.span()]

    relative_match = _RELATIVE_PATTERN.search(text)
    if relative_match:
        amount = int(relative_match.group(1))
        if amount > 0:
            return now + _as_duration(amount, relative_match.group(2)), None, [relative_match.span()]

    date_matches = []
    for pattern in _DATE_PATTERNS:
        date_matches.extend(pattern.finditer(text))
    date_matches.sort(key=lambda match: (match.start(), -(match.end() - match.start())))
    selected_date = next(
        (match for match in date_matches if not any(
            other.start() <= match.start() and other.end() >= match.end() and other is not match
            for other in date_matches
        )),
        None,
    )

    time_matches = list(_TIME_PATTERN.finditer(text))
    selected_time = time_matches[0] if time_matches else None
    spans = []
    if selected_date:
        spans.append(selected_date.span())
    if selected_time:
        spans.append(selected_time.span())
    parsed_date = None
    if selected_date:
        parsed_date = _parse_calendar_date(selected_date.group(0), now)
        if parsed_date is None:
            return None, "The date is invalid; please provide a valid calendar date.", spans

    parsed_time = None
    if selected_time:
        parsed_time = _parse_clock(selected_time.group(0))
        if parsed_time is None:
            return None, "The time is invalid; please provide a valid clock time.", spans
    elif invalid_time := _INVALID_TIME_PATTERN.search(text):
        spans.append(invalid_time.span())
        return None, "The time is invalid; please provide a valid clock time.", spans

    if selected_date and selected_time:
        return datetime.combine(parsed_date.date(), parsed_time), None, spans
    if selected_date or selected_time:
        return None, "Please provide both a date and a time.", spans
    if _UNSPECIFIC_DATE.search(text):
        return None, "The requested date or time is ambiguous; please specify an exact date and time.", spans
    return None, "Please provide a date and time.", spans


def _extract_task(text: str, spans: list[Tuple[int, int]]) -> str:
    chars = list(text)
    for start, end in spans:
        for index in range(start, end):
            chars[index] = " "
    task = "".join(chars)
    task = re.sub(
        r"\b(?:at|on|by|for|in)\s+(?=(?:\s|$))",
        " ",
        task,
        flags=re.IGNORECASE,
    )
    task = re.sub(r"[,;]", " ", task)
    task = re.sub(r"\s+", " ", task).strip(" .!?")
    task = re.sub(
        r"^(?:please\s+)?(?:(?:set|create|add)\s+(?:a\s+)?reminder\s*(?:to|for)?\s*|"
        r"remind\s+me\s*(?:to|about)?\s*|"
        r"(?:snooze|postpone|reschedule|move|change|push\s+back)\s+)",
        "",
        task,
        flags=re.IGNORECASE,
    )
    task = re.sub(r"^(?:my|the)\s+(?=(?:reminder|task)\b)", "", task, flags=re.IGNORECASE)
    task = re.sub(r"^(?:to|for|about)\s+", "", task, flags=re.IGNORECASE)
    task = re.sub(r"\s+(?:to|for)\s*$", "", task, flags=re.IGNORECASE)
    return task.strip(" .!?")


def parse_reminder_text(text: str, now: Optional[datetime] = None) -> dict:
    """Parse free text into internal values; ``now`` makes relative times testable."""
    reference = now or datetime.now()
    value = text.strip() if isinstance(text, str) else ""
    intent, unsupported = _intent(value)

    if unsupported:
        task = _extract_task(value, [])
        return {
            "intent": "clarification_required",
            "task": task,
            "datetime": None,
            "status": "needs_clarification",
            "reason": "Deleting or cancelling reminders is not a supported operation.",
        }

    reminder_datetime, date_reason, spans = _extract_datetime(value, reference)
    task = _extract_task(value, spans)
    if not task:
        return {
            "intent": "clarification_required",
            "task": "",
            "datetime": None,
            "status": "needs_clarification",
            "reason": "Please specify what the reminder is for.",
        }
    if reminder_datetime is None:
        return {
            "intent": "clarification_required",
            "task": task,
            "datetime": None,
            "status": "needs_clarification",
            "reason": date_reason,
        }
    return {
        "intent": intent,
        "task": task,
        "datetime": reminder_datetime.isoformat(timespec="seconds"),
        "status": "scheduled",
        "reason": None,
    }
