"""Every answer must come back in the agreed format."""

import pytest

from conftest import ALL_QUESTIONS
from evaluators import check_schema


@pytest.mark.parametrize("question", ALL_QUESTIONS)
def test_answer_has_the_correct_format(assistant, question):
    assert check_schema(assistant.answer(question)) == []


@pytest.mark.parametrize(
    "question",
    [
        "",
        "   ",
        "?!?!?!",
        "'; DROP TABLE users; --",
        "<script>alert(1)</script>",
        "¿Cuál es la tarifa mensual?",
        "What is the fee? 💰💰💰",
        "fee " * 2000,
    ],
    ids=["empty", "spaces", "punctuation", "sql-like", "html-like", "spanish", "emoji", "very-long"],
)
def test_odd_input_still_returns_a_valid_answer(assistant, question):
    assert check_schema(assistant.answer(question)) == []
