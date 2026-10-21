"""Unit tests for the schema evaluator's edge cases."""

import pytest

from evaluators import check_schema


def result(**overrides):
    base = {"answer": "text", "citations": ["1.1"], "refused": False}
    base.update(overrides)
    return base


def test_valid_answered_result_passes():
    assert check_schema(result()) == []


def test_valid_refused_result_passes():
    assert check_schema(result(answer="No.", citations=[], refused=True)) == []


@pytest.mark.parametrize("not_a_dict", [None, "text", ["answer"], 42])
def test_non_dict_result_fails(not_a_dict):
    assert check_schema(not_a_dict) == ["Answer is not a dict."]


def test_missing_keys_fail():
    assert check_schema({"answer": "text"}) == [
        "'citations' must be a list of strings.",
        "'refused' must be true or false.",
    ]


def test_citations_as_a_string_fail():
    assert check_schema(result(citations="1.1")) == ["'citations' must be a list of strings."]


def test_refused_as_a_string_fails():
    assert check_schema(result(refused="no")) == ["'refused' must be true or false."]


def test_refused_answer_must_not_cite():
    assert check_schema(result(refused=True)) == ["A refused answer must not cite any section."]


def test_answer_without_citation_fails():
    assert check_schema(result(citations=[])) == ["An answer must cite at least one section."]


def test_empty_answer_text_fails():
    assert check_schema(result(answer="  ")) == ["An answer must not be empty."]
