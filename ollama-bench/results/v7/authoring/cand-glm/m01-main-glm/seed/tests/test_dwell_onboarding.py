"""Confirms the dwell-onboarding cutoff cited by RN-0212.

See docs/release-notes/RN-0212-dwell-onboarding.md.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from helpers.dwell_checks import DWELL_ONBOARDING_CUTOFF, onboarded_in_scope  # noqa: E402


def test_cutoff_matches_the_release_note():
    assert DWELL_ONBOARDING_CUTOFF == "2034-04-01"


def test_onboarded_in_scope_boundary():
    assert onboarded_in_scope("2034-04-01")
    assert not onboarded_in_scope("2034-03-31")
