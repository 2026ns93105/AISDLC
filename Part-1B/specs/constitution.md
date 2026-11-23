# Natural Language Reminder Agent Constitution

## Mission
Provide a small, predictable assistant that converts a user's reminder request into one structured JSON object. The implementation is rule-based and never invents missing date or time information.

## Principles
1. **Correctness before convenience:** requests that lack a task, a complete date/time, or have an invalid date must ask for clarification.
2. **Constrained output:** only `create_reminder`, `reschedule_reminder`, `snooze_reminder`, and `clarification_required` are valid intents.
3. **Transparent uncertainty:** ambiguous, unsupported, or invalid requests return a useful `reason` rather than a guessed reminder.
4. **Machine-readable interface:** every response contains exactly the required fields and can be serialized as valid JSON.
5. **Local and reproducible:** date interpretation uses the system's local time unless a test or caller injects a reference time; no network or language-model service is required.
6. **Testable quality:** changes must preserve the schema, invariants, and behavior covered by the evaluation dataset.

## Change discipline
Changes to intent values, output fields, date interpretation, or clarification behavior require updating the specification, tests, and evaluation data together. The test suite and evaluation runner must pass before a change is considered complete.
