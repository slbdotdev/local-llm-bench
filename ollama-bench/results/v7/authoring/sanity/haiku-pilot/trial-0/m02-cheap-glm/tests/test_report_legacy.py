"""Legacy buyer-summary tests, still pinned to the pre-refactor entry point.

These fail while the report.py refactor is in flight; they will be ported
to render_summary as part of the refactor (scratch/refactor-notes.md,
step 4).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))

from quartermaster.report import render_legacy_summary  # noqa: E402,F401


def test_legacy_summary_renders():
    assert callable(render_legacy_summary)
