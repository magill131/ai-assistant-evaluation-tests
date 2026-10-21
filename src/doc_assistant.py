"""A small document Q&A assistant: the system under test.

It answers questions about a short service agreement by finding the section
that shares the most meaningful words with the question and quoting it. If no
section shares at least two meaningful words, it refuses.

Every answer is a dict:
    {"answer": str, "citations": [section ids], "refused": bool}

This is a rule-based stand-in for an AI assistant so the evaluation tests can
run offline and give the same result every time. The evaluators in
evaluators.py only look at the answer dict, so they would work the same way on
a real model's output.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

REFUSAL_MESSAGE = (
    "I can only answer questions about the agreement, and I could not find "
    "that in it."
)

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "does",
    "for", "from", "how", "i", "if", "in", "is", "it", "its", "me", "my",
    "of", "on", "or", "s", "so", "that", "the", "this", "to", "was", "what",
    "when", "where", "which", "who", "will", "with", "you", "your",
}

_SUFFIXES = ("ation", "ated", "ate", "ing", "ed", "ly", "es", "s")


def load_document(path: Path | None = None) -> dict:
    path = path or DATA_DIR / "sample_agreement.json"
    return json.loads(Path(path).read_text(encoding="utf-8"))


def stem(word: str) -> str:
    for suffix in _SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {stem(w) for w in words if w not in STOPWORDS}


class DocAssistant:
    min_overlap = 2

    def __init__(self, document: dict | None = None):
        self.document = document or load_document()

    def answer(self, question: str) -> dict:
        question_tokens = tokenize(question)

        # Rank by score, then by how much of the section the question covers
        # (a short section that matches fully beats a long one that matches
        # the same number of words), then by section ID so results are stable.
        best_id, best_rank, best_overlap = None, None, 0
        for section_id in sorted(self.document):
            section = self.document[section_id]
            body_tokens = tokenize(section["title"] + " " + section["text"])
            title_tokens = tokenize(section["title"])
            overlap = len(question_tokens & body_tokens)
            score = overlap + len(question_tokens & title_tokens)
            coverage = overlap / len(body_tokens) if body_tokens else 0.0
            rank = (score, coverage)
            if best_rank is None or rank > best_rank:
                best_id, best_rank, best_overlap = section_id, rank, overlap

        if best_id is None or best_overlap < self.min_overlap:
            return {"answer": REFUSAL_MESSAGE, "citations": [], "refused": True}

        return {
            "answer": self.document[best_id]["text"],
            "citations": [best_id],
            "refused": False,
        }
