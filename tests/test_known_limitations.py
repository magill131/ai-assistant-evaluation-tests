"""Known weaknesses of the assistant, written as expected failures.

Each test describes the behavior we want. It is marked xfail (strict), so the
suite stays green today, and the moment someone fixes the weakness the test
starts passing and strict mode fails the run, which is the signal to remove
the marker.
"""

import pytest

from evaluators import check_expected, check_refusal


@pytest.mark.xfail(
    reason="Assistant matches on shared words only, so it answers about a different company's fee."
)
def test_question_about_a_different_company_is_refused(assistant):
    result = assistant.answer("What is the monthly fee for Netflix?")
    assert check_refusal(result) == []


@pytest.mark.xfail(
    reason="Assistant has no synonyms: 'contract' is not understood to mean 'agreement'."
)
def test_synonym_for_agreement_finds_the_renewal_section(assistant):
    result = assistant.answer("Does the contract renew by itself?")
    assert check_expected(result, "1.2", "12 months") == []
