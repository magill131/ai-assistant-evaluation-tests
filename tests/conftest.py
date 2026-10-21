import pytest

from doc_assistant import DocAssistant, load_document
from evaluation import load_json


@pytest.fixture(scope="session")
def document():
    return load_document()


@pytest.fixture(scope="session")
def assistant():
    return DocAssistant()


GOLDEN = load_json("golden_questions.json")
OUT_OF_SCOPE = load_json("out_of_scope_questions.json")
GROUPS = load_json("paraphrase_groups.json")

ALL_QUESTIONS = [case["question"] for case in GOLDEN] + OUT_OF_SCOPE
