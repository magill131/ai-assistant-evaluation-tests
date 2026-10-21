"""Golden set: questions with a known correct section and a known correct fact."""

import pytest

from conftest import GOLDEN
from evaluators import check_expected


@pytest.mark.parametrize("case", GOLDEN, ids=[c["id"] for c in GOLDEN])
def test_golden_question_gets_the_expected_answer(assistant, case):
    result = assistant.answer(case["question"])
    assert check_expected(result, case["expected_section"], case["expected_fact"]) == []


def test_every_section_in_the_agreement_is_covered_by_a_golden_question(document):
    covered = {case["expected_section"] for case in GOLDEN}
    assert covered == set(document)
