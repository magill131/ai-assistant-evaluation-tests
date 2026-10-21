"""Cited sections must exist, and answers must cite something."""

import pytest

from conftest import ALL_QUESTIONS, GOLDEN
from evaluators import check_citations


@pytest.mark.parametrize("question", ALL_QUESTIONS)
def test_every_cited_section_exists(assistant, document, question):
    assert check_citations(assistant.answer(question), document) == []


@pytest.mark.parametrize("case", GOLDEN, ids=[c["id"] for c in GOLDEN])
def test_answered_questions_cite_exactly_one_section(assistant, case):
    result = assistant.answer(case["question"])
    assert len(result["citations"]) == 1


def test_citation_check_flags_a_section_that_does_not_exist(document):
    fake = {"answer": "Yes.", "citations": ["9.9"], "refused": False}
    assert check_citations(fake, document) == ["Cited section 9.9 does not exist."]
