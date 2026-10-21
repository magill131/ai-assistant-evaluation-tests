"""Run an assistant over the test data and compute quality metrics."""

from __future__ import annotations

import json
from pathlib import Path

from doc_assistant import DATA_DIR, load_document
from evaluators import (
    check_citations,
    check_consistent,
    check_expected,
    check_grounded,
    check_refusal,
    check_schema,
)

ROOT = Path(__file__).resolve().parent.parent


def load_json(name: str):
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def load_thresholds() -> dict:
    return json.loads((ROOT / "thresholds.json").read_text(encoding="utf-8"))


def _rate(passed: int, total: int) -> float:
    return round(passed / total, 3) if total else 1.0


def compute_metrics(assistant) -> dict:
    document = load_document()
    golden = load_json("golden_questions.json")
    out_of_scope = load_json("out_of_scope_questions.json")
    groups = load_json("paraphrase_groups.json")

    golden_results = [assistant.answer(case["question"]) for case in golden]
    oos_results = [assistant.answer(q) for q in out_of_scope]

    all_results = golden_results + oos_results
    schema_ok = sum(1 for r in all_results if not check_schema(r))
    citation_ok = sum(1 for r in all_results if not check_citations(r, document))
    grounded_ok = sum(1 for r in golden_results if not check_grounded(r, document))
    golden_ok = sum(
        1
        for case, r in zip(golden, golden_results)
        if not check_expected(r, case["expected_section"], case["expected_fact"])
    )
    refusal_ok = sum(1 for r in oos_results if not check_refusal(r))
    consistent_ok = sum(
        1
        for group in groups
        if not check_consistent(
            [assistant.answer(q) for q in group["questions"]],
            group["expected_section"],
        )
    )

    return {
        "schema_valid_rate": _rate(schema_ok, len(all_results)),
        "citation_valid_rate": _rate(citation_ok, len(all_results)),
        "grounded_rate": _rate(grounded_ok, len(golden_results)),
        "golden_accuracy": _rate(golden_ok, len(golden)),
        "refusal_rate": _rate(refusal_ok, len(oos_results)),
        "consistency_rate": _rate(consistent_ok, len(groups)),
    }


def failed_thresholds(metrics: dict, thresholds: dict) -> list[str]:
    return [
        f"{name}: {metrics[name]} is below {minimum}"
        for name, minimum in thresholds.items()
        if metrics[name] < minimum
    ]
