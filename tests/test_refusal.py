"""Out-of-scope questions must be refused, with nothing cited."""

import pytest

from conftest import OUT_OF_SCOPE
from doc_assistant import REFUSAL_MESSAGE
from evaluators import check_refusal


@pytest.mark.parametrize("question", OUT_OF_SCOPE)
def test_out_of_scope_question_is_refused(assistant, question):
    assert check_refusal(assistant.answer(question)) == []


@pytest.mark.parametrize("question", OUT_OF_SCOPE)
def test_refusal_uses_the_standard_message(assistant, question):
    assert assistant.answer(question)["answer"] == REFUSAL_MESSAGE


@pytest.mark.parametrize("question", ["", "   ", "?!?!", "'; DROP TABLE users; --"])
def test_empty_or_junk_input_is_refused(assistant, question):
    assert check_refusal(assistant.answer(question)) == []


def test_refusal_check_flags_an_assistant_that_answers_anyway():
    fake = {"answer": "Yes, it is covered.", "citations": ["1.1"], "refused": False}
    assert check_refusal(fake) == [
        "Assistant answered a question it should have refused.",
        "Assistant cited sections for an out-of-scope question.",
    ]
