"""The same question worded differently must get the same answer."""

import pytest

from conftest import GROUPS
from evaluators import check_consistent


@pytest.mark.parametrize("group", GROUPS, ids=[g["id"] for g in GROUPS])
def test_different_wordings_cite_the_same_section(assistant, group):
    results = [assistant.answer(q) for q in group["questions"]]
    assert check_consistent(results, group["expected_section"]) == []


def test_same_question_twice_gives_the_same_answer(assistant):
    question = "What is the monthly fee?"
    assert assistant.answer(question) == assistant.answer(question)


@pytest.mark.parametrize(
    "variant",
    ["WHAT IS THE MONTHLY FEE?", "what is the monthly fee", "  What is the monthly fee???  "],
    ids=["upper", "no-punctuation", "extra-spaces-and-marks"],
)
def test_capitalization_and_punctuation_do_not_change_the_answer(assistant, variant):
    assert assistant.answer(variant) == assistant.answer("What is the monthly fee?")
