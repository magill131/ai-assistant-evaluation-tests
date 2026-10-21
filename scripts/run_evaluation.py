"""Run the evaluation and write a metrics report.

Scores the real assistant and three deliberately broken ones side by side, writes
docs/evaluation_report.md and docs/evaluation_report.json, and exits with code 1
if the real assistant is below any threshold in thresholds.json. This is the
quality gate CI runs after the tests.

Run it with:  python scripts/run_evaluation.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]

from bad_assistants import BAD_ASSISTANTS  # noqa: E402
from doc_assistant import DocAssistant  # noqa: E402
from evaluation import compute_metrics, failed_thresholds, load_thresholds  # noqa: E402

LABELS = {
    "schema_valid_rate": "Answers in the correct format",
    "citation_valid_rate": "Citations point to real sections",
    "grounded_rate": "Figures match the cited section",
    "golden_accuracy": "Golden questions answered correctly",
    "refusal_rate": "Out-of-scope questions refused",
    "consistency_rate": "Reworded questions get the same answer",
}


def pct(value: float) -> str:
    return f"{value * 100:.0f}%"


def main() -> int:
    thresholds = load_thresholds()
    assistants = {"Assistant": DocAssistant()}
    assistants.update({name: cls() for name, cls in BAD_ASSISTANTS.items()})

    scores = {name: compute_metrics(a) for name, a in assistants.items()}
    problems = failed_thresholds(scores["Assistant"], thresholds)

    names = list(scores)
    lines = [
        "# Evaluation report",
        "",
        "The real assistant is scored next to three deliberately broken ones. "
        "The broken ones should fail, which shows the checks can tell good "
        "answers from bad ones.",
        "",
        "| Metric | Minimum | " + " | ".join(names) + " |",
        "|---|---|" + "|".join(["---"] * len(names)) + "|",
    ]
    for key, label in LABELS.items():
        row = [label, pct(thresholds[key])]
        for name in names:
            row.append(pct(scores[name][key]))
        lines.append("| " + " | ".join(row) + " |")
    lines += [
        "",
        "Result for the real assistant: "
        + ("PASS, every metric meets its minimum." if not problems else "FAIL."),
    ]

    docs = ROOT / "docs"
    docs.mkdir(exist_ok=True)
    (docs / "evaluation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (docs / "evaluation_report.json").write_text(
        json.dumps({"thresholds": thresholds, "scores": scores}, indent=2) + "\n",
        encoding="utf-8",
    )

    print("\n".join(lines))
    if problems:
        print("\nEvaluation gate FAILED:")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("\nEvaluation gate passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
