"""Deliberately broken assistants.

They exist to prove the evaluators and thresholds catch real problems. If an
evaluator could not tell these apart from the good assistant, it would be
useless.
"""

from __future__ import annotations

import re

from doc_assistant import DocAssistant


class HallucinatingAssistant(DocAssistant):
    """Finds the right section but changes every number in the answer."""

    def answer(self, question: str) -> dict:
        result = super().answer(question)
        if not result["refused"]:
            result["answer"] = re.sub(
                r"\d+", lambda m: str(int(m.group()) + 1), result["answer"]
            )
        return result


class OverconfidentAssistant(DocAssistant):
    """Never refuses. Makes up an answer and cites a section that does not exist."""

    def answer(self, question: str) -> dict:
        result = super().answer(question)
        if result["refused"]:
            return {
                "answer": "Yes, that is covered in the agreement.",
                "citations": ["9.9"],
                "refused": False,
            }
        return result


class BrokenFormatAssistant(DocAssistant):
    """Returns the wrong keys and types."""

    def answer(self, question: str) -> dict:
        result = super().answer(question)
        return {"answer": result["answer"], "sources": ", ".join(result["citations"])}


BAD_ASSISTANTS = {
    "Hallucinating": HallucinatingAssistant,
    "Overconfident": OverconfidentAssistant,
    "Broken format": BrokenFormatAssistant,
}
