# Evaluation Harness Log

The runner uses a fixed reference time (`2026-11-23T10:00:00`) so relative dates are reproducible. It validates each response in three independent layers: schema/datatype validation, business invariants, and expected intent/task semantics. The aggregate score is `(schema passes + invariant passes + semantic passes) / (3 × total cases) × 100`; an overall case is passed only when all three layers pass.

Run `python .harness/evaluation_runner.py` to regenerate `eval-results.json`. The result file contains per-case outputs and diagnostics as well as the requested `total_cases`, `passed`, `failed`, and percentage `score` summary.
