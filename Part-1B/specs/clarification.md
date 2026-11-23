# Clarification and Assumptions

## Resolved decisions
1. **No external AI service:** use deterministic parsing so output is reproducible and no request text leaves the machine.
2. **Local timezone:** output datetimes are local ISO 8601 values without a timezone suffix. Callers that need a timezone-aware value must provide that context outside this minimal agent.
3. **Missing year:** month-name dates without a year resolve to the next upcoming calendar occurrence. This is an explicit parsing convention, not a guessed missing day or time.
4. **Weekday interpretation:** an unqualified weekday is the next occurrence (today if it is that weekday); `next <weekday>` is the occurrence in the following week.
5. **Relative expressions:** an explicit duration such as `in 2 hours` or `snooze for 10 minutes` is resolved against the agent's injected or current local reference time.
6. **Ambiguous timing:** expressions without an exact supported date/time (such as `later`, `soon`, or `next week`) are not scheduled.
7. **Output format:** the Python API returns a dictionary; the CLI serializes that dictionary to JSON. Clarifications use a null datetime and a human-readable reason.

## Out of scope
Persistence, notifications, timezone conversion, recurring reminders, editing/deleting reminders, and external calendar integration are not implemented. Unsupported operations are safely routed to clarification.

## Risks and mitigations
- Natural language is open-ended: support a documented set of date/time forms and ask for clarification otherwise.
- Local clock dependence affects relative-time tests: inject a fixed reference datetime in tests and evaluations.
- Task extraction can be imperfect for unusual syntax: prefer a clarification to fabricating a task; cover representative phrasings with regression cases.
