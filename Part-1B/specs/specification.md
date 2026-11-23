# Product Specification

## Overview
The Natural Language Reminder Agent accepts one free-text request and returns one structured reminder response. It is implemented as a deterministic Python program with a command-line interface.

## Supported intents
- `create_reminder`: create a new reminder.
- `reschedule_reminder`: change the date/time of an existing reminder.
- `snooze_reminder`: defer an existing reminder.
- `clarification_required`: the request cannot safely be completed.

Unsupported actions (for example deleting or cancelling a reminder) use `clarification_required`; the agent does not claim to perform them.

## Response contract
Responses have exactly these fields:

```json
{
  "intent": "create_reminder",
  "task": "call Alex",
  "datetime": "2026-11-24T15:00:00",
  "status": "scheduled",
  "reason": null
}
```

`intent`, `task`, and `status` are strings. `datetime` is an ISO 8601 local date-time string or `null`. `reason` is a string or `null`. Successful responses use status `scheduled`; clarification responses use `needs_clarification` and a non-empty reason. The CLI writes only JSON to standard output.

## Date and time interpretation
The parser recognizes ISO dates, common numeric dates, month-name dates, `today`, `tomorrow`, `day after tomorrow`, weekdays, and explicit clock times in 12-hour or 24-hour form. It also recognizes simple relative intervals (`in 2 days`, `in 3 hours`) and snooze durations (`for 10 minutes`). Date-only or time-only requests are incomplete. An omitted year in a month-name date means the next upcoming occurrence. Weekday names without `next` mean the next occurrence, including today; `next <weekday>` means the following week's occurrence. Relative intervals and snooze durations are calculated from the supplied reference time or the local system clock.

The agent does not infer a clock time for an all-day date, nor a date from a clock time alone. Ambiguous phrases such as `sometime next week` are not converted into an arbitrary timestamp. Invalid calendar dates or clock values trigger clarification.

## Clarification rules
Clarification is required when the task is absent, the request has no date/time or only one component, the date/time is ambiguous or invalid, or the requested operation is unsupported. No successful response is emitted unless a non-empty task and a valid date/time were extracted.

## Acceptance Criteria
- **AC1:** Every result is valid JSON and conforms to the response schema.
- **AC2:** All five required fields are present with valid data types.
- **AC3:** Missing critical information triggers `clarification_required`.
- **AC4:** Only supported intents are returned.
- **AC5:** The agent does not hallucinate datetime information; it only uses explicit or supported relative date/time expressions.
- **AC6:** The evaluation runner exercises at least 15 diverse cases and persists its results.
- **AC7:** The test suite and evaluation runner execute locally without network access.
