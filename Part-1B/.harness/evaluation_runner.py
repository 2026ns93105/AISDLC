"""Run all evaluation cases and write the aggregate evaluation report."""

import json
import os
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import process_request
from invariant_validator import validate_invariants
from schema_validator import validate_schema
from semantic_evaluator import evaluate_semantics


def run_evaluations():
    dataset_path = os.path.join(ROOT, "evals", "dataset.json")
    output_path = os.path.join(ROOT, "evidence", "eval-results.json")
    with open(dataset_path, "r", encoding="utf-8") as dataset_file:
        cases = json.load(dataset_file)

    reference_time = datetime(2026, 11, 23, 10, 0, 0)
    results = []
    schema_pass = invariant_pass = semantic_pass = passed = 0
    for index, case in enumerate(cases, start=1):
        response = process_request(case["input"], now=reference_time)
        schema_ok, schema_errors = validate_schema(response)
        invariant_ok, invariant_errors = validate_invariants(response)
        semantic_ok, semantic_errors = evaluate_semantics(case, response)
        schema_pass += int(schema_ok)
        invariant_pass += int(invariant_ok)
        semantic_pass += int(semantic_ok)
        case_passed = schema_ok and invariant_ok and semantic_ok
        passed += int(case_passed)
        results.append({
            "case": index,
            "input": case["input"],
            "passed": case_passed,
            "response": response,
            "checks": {
                "schema": {"passed": schema_ok, "errors": schema_errors},
                "invariants": {"passed": invariant_ok, "errors": invariant_errors},
                "semantic": {"passed": semantic_ok, "errors": semantic_errors},
            },
        })

    total = len(cases)
    score = 100.0 * (schema_pass + invariant_pass + semantic_pass) / (3 * total) if total else 0.0
    report = {
        "total_cases": total,
        "passed": passed,
        "failed": total - passed,
        "score": round(score, 2),
        "threshold": 80,
        "result": "PASS" if score >= 80 else "FAIL",
        "layer_passes": {
            "schema": schema_pass,
            "invariants": invariant_pass,
            "semantic": semantic_pass,
        },
        "cases": results,
    }
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(report, output_file, indent=2, ensure_ascii=False)
        output_file.write("\n")
    return report


if __name__ == "__main__":
    result = run_evaluations()
    print(json.dumps({
        "total_cases": result["total_cases"],
        "passed": result["passed"],
        "failed": result["failed"],
        "score": result["score"],
        "result": result["result"],
    }, indent=2))
    raise SystemExit(0 if result["result"] == "PASS" else 1)
