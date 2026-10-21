"""Evaluators for assistant answers.

Each evaluator takes an answer dict and returns a list of problems. An empty
list means the answer passed that check.
"""

from __future__ import annotations

import re

NUMBER_PATTERN = re.compile(r"\$?\d[\d,]*(?:\.\d+)?%?")


def check_schema(result) -> list[str]:
    """The answer must be a dict with the right keys and types."""
    if not isinstance(result, dict):
        return ["Answer is not a dict."]

    problems = []
    if not isinstance(result.get("answer"), str):
        problems.append("'answer' must be a string.")
    citations = result.get("citations")
    if not isinstance(citations, list) or not all(isinstance(c, str) for c in citations):
        problems.append("'citations' must be a list of strings.")
    if not isinstance(result.get("refused"), bool):
        problems.append("'refused' must be true or false.")
    if problems:
        return problems

    if result["refused"] and result["citations"]:
        problems.append("A refused answer must not cite any section.")
    if not result["refused"]:
        if not result["citations"]:
            problems.append("An answer must cite at least one section.")
        if not result["answer"].strip():
            problems.append("An answer must not be empty.")
    return problems


def check_citations(result, document: dict) -> list[str]:
    """Every cited section must exist in the document."""
    if check_schema(result):
        return ["Cannot check citations: answer has the wrong format."]
    return [
        f"Cited section {section_id} does not exist."
        for section_id in result["citations"]
        if section_id not in document
    ]


def _numbers(text: str) -> set[str]:
    return {m.group().rstrip(".,") for m in NUMBER_PATTERN.finditer(text)}


def check_grounded(result, document: dict) -> list[str]:
    """Every number, dollar amount and percentage in the answer must appear
    in the sections it cites."""
    if check_schema(result) or check_citations(result, document):
        return ["Cannot check grounding: answer or citations are invalid."]
    if result["refused"]:
        return []

    source_text = " ".join(document[c]["text"] for c in result["citations"])
    source_numbers = _numbers(source_text)
    return [
        f"'{number}' is in the answer but not in the cited sections."
        for number in sorted(_numbers(result["answer"]) - source_numbers)
    ]


def check_refusal(result) -> list[str]:
    """For a question the document cannot answer, the assistant must refuse
    and cite nothing."""
    if check_schema(result):
        return ["Cannot check refusal: answer has the wrong format."]
    problems = []
    if not result["refused"]:
        problems.append("Assistant answered a question it should have refused.")
    if result["citations"]:
        problems.append("Assistant cited sections for an out-of-scope question.")
    return problems


def check_expected(result, expected_section: str, expected_fact: str) -> list[str]:
    """The answer must cite the expected section and contain the expected fact."""
    if check_schema(result):
        return ["Cannot check answer: answer has the wrong format."]
    problems = []
    if result["refused"]:
        problems.append("Assistant refused a question it should have answered.")
        return problems
    if expected_section not in result["citations"]:
        problems.append(
            f"Expected section {expected_section}, got {result['citations']}."
        )
    if expected_fact.lower() not in result["answer"].lower():
        problems.append(f"Expected the answer to contain '{expected_fact}'.")
    return problems


def check_consistent(results: list, expected_section: str) -> list[str]:
    """Different wordings of the same question must cite the same section."""
    problems = []
    for index, result in enumerate(results):
        if check_schema(result):
            problems.append(f"Wording {index + 1} returned the wrong format.")
        elif result["citations"] != [expected_section]:
            problems.append(
                f"Wording {index + 1} cited {result['citations']}, "
                f"expected [{expected_section!r}]."
            )
    return problems
