"""Numbers, dollar amounts and percentages in an answer must come from the
section it cites. An assistant must not make up figures."""

import pytest

from conftest import GOLDEN
from evaluators import check_grounded


@pytest.mark.parametrize("case", GOLDEN, ids=[c["id"] for c in GOLDEN])
def test_answer_only_contains_figures_from_the_cited_section(assistant, document, case):
    assert check_grounded(assistant.answer(case["question"]), document) == []


def test_grounding_check_flags_a_changed_dollar_amount(document):
    fake = {
        "answer": "The client pays a monthly fee of $3,000, due on the 5th day of each month.",
        "citations": ["2.1"],
        "refused": False,
    }
    assert check_grounded(fake, document) == [
        "'$3,000' is in the answer but not in the cited sections."
    ]


def test_grounding_check_flags_a_changed_percentage(document):
    fake = {
        "answer": "Payments more than 15 days late incur a late fee of 5% of the unpaid amount.",
        "citations": ["2.2"],
        "refused": False,
    }
    assert check_grounded(fake, document) == [
        "'5%' is in the answer but not in the cited sections."
    ]


def test_grounding_check_passes_when_figures_match(document):
    real = {
        "answer": document["2.1"]["text"],
        "citations": ["2.1"],
        "refused": False,
    }
    assert check_grounded(real, document) == []


def test_figures_from_a_different_section_do_not_count(document):
    # 24 months is in section 1.1, but this answer cites 2.1.
    fake = {"answer": "The fee runs for 24 months.", "citations": ["2.1"], "refused": False}
    assert check_grounded(fake, document) == [
        "'24' is in the answer but not in the cited sections."
    ]
