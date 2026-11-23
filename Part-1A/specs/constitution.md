# Smart Todo Manager Constitution

## Purpose

Smart Todo Manager is a small, reliable Python application for creating and
maintaining personal tasks in a readable JSON file.

## Principles

1. **Correctness first:** Validate task values at the application boundary and
   preserve a single, documented task schema.
2. **Persistent by default:** Successful create, update, status, and delete
   operations are reflected in `tasks.json`.
3. **Clear failures:** Invalid input, malformed persisted data, and storage
   failures must be reported rather than silently ignored.
4. **Simple and maintainable:** Use the Python standard library for application
   behavior and keep public operations reusable and documented.
5. **Verifiable behavior:** Automated tests cover the acceptance criteria and
   the harness runs lint, security, and test checks.

## Data Integrity

Task IDs are positive integers and unique within the store. Priority and status
values are restricted to the choices defined in the specification. Writes are
validated and performed through a temporary file before replacing the target.

## Quality Bar

The project targets Python 3, follows PEP 8, and must pass Ruff, Bandit, and
pytest using the supplied harness.
