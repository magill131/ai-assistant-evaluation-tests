"""Test the tests: broken assistants must be caught, the good one must pass."""

import pytest

from bad_assistants import (
    BAD_ASSISTANTS,
    BrokenFormatAssistant,
    HallucinatingAssistant,
    OverconfidentAssistant,
)
from conftest import GOLDEN, OUT_OF_SCOPE
from doc_assistant import DocAssistant, load_document
from evaluation import compute_metrics, failed_thresholds, load_thresholds
from evaluators import check_citations, check_grounded, check_refusal, check_schema


def test_good_assistant_meets_every_threshold():
    metrics = compute_metrics(DocAssistant())
    assert failed_thresholds(metrics, load_thresholds()) == []


@pytest.mark.parametrize("name", BAD_ASSISTANTS)
def test_every_bad_assistant_fails_at_least_one_threshold(name):
    metrics = compute_metrics(BAD_ASSISTANTS[name]())
    assert failed_thresholds(metrics, load_thresholds()) != []


# Only sections that contain a figure can have a figure changed.
GOLDEN_WITH_FIGURES = [
    case
    for case in GOLDEN
    if any(ch.isdigit() for ch in load_document()[case["expected_section"]]["text"])
]


@pytest.mark.parametrize(
    "case", GOLDEN_WITH_FIGURES, ids=[c["id"] for c in GOLDEN_WITH_FIGURES]
)
def test_hallucinated_numbers_are_flagged(document, case):
    result = HallucinatingAssistant().answer(case["question"])
    assert check_grounded(result, document) != []


@pytest.mark.parametrize("question", OUT_OF_SCOPE)
def test_overconfident_answers_are_flagged(document, question):
    result = OverconfidentAssistant().answer(question)
    assert check_refusal(result) != []
    assert check_citations(result, document) == ["Cited section 9.9 does not exist."]


@pytest.mark.parametrize("case", GOLDEN[:5], ids=[c["id"] for c in GOLDEN[:5]])
def test_wrong_format_is_flagged(case):
    result = BrokenFormatAssistant().answer(case["question"])
    problems = check_schema(result)
    assert "'citations' must be a list of strings." in problems
    assert "'refused' must be true or false." in problems
