# Implementation Plan

1. Define the response contract, supported intents, date grammar, and clarification behavior.
2. Implement a standard-library parser that extracts intent, task, and a complete explicit or supported relative datetime.
3. Implement an agent API that enforces the contract and exposes a JSON command-line interface.
4. Add schema, invariant, and semantic evaluation layers with a deterministic dataset of diverse cases.
5. Add pytest coverage for successful parsing and critical clarification/guardrail paths.
6. Run unit tests and the evaluation runner; save the resulting evidence and record the outcome.

## Verification
The project is complete when `python -m pytest -q` passes and `python .harness/evaluation_runner.py` completes all dataset rows, writes `evidence/eval-results.json`, and reports a score of at least 80%.
