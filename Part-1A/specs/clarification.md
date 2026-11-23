# Clarification Record

The functional brief did not define function signatures, default values, tag
matching behavior, or missing-task behavior. The following decisions make the
interface predictable and testable:

1. IDs are positive integers and must be unique.
2. New tasks default to `Medium` priority, `Pending` status, an empty
   description, and no tags.
3. Tag filtering ignores letter case and trims surrounding whitespace.
4. An update of a nonexistent ID raises `KeyError`; deletion of a nonexistent
   ID returns `False`.
5. Updates are limited to title, description, priority, status, and tags. At
   least one update field is required.
6. A missing task file represents an empty task list. Invalid JSON or invalid
   task values raise `ValueError`; values supplied using the wrong Python type
   raise `TypeError`.
7. JSON is a top-level array of task objects; writes are validated and
   atomically replace the previous file.
8. The command-line interface uses subcommands and prints JSON results.

These clarifications preserve the requested schema and keep the API suitable
for both direct Python use and command-line operation.
