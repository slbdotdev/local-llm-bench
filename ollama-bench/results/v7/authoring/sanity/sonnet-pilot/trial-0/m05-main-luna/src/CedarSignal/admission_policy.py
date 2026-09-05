"""admission_policy: handoff policy for the CedarSignal pipeline.

This small policy component is intentionally independent of the generated stages. Its
implementation is the authority for the corresponding documentation.
"""

from __future__ import annotations

DEFAULT_ADMISSION_LIMIT = 18
DEFAULT_ADMISSION_WINDOW_S = 75
ADMISSION_STATES = ("pending", "held", "settled", "abandoned")


def policy_defaults():
    """Return the implementation's defaults for a handoff admission window."""
    return {
        "limit": DEFAULT_ADMISSION_LIMIT,
        "window_s": DEFAULT_ADMISSION_WINDOW_S,
    }


def lifecycle_states():
    """Return states in their implementation-defined lifecycle order."""
    return ADMISSION_STATES
