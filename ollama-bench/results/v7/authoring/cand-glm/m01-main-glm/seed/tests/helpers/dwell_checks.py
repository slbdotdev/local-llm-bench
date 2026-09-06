"""Small helper for the dwell-onboarding exemption.

See docs/release-notes/RN-0212-dwell-onboarding.md: a stage is only in scope for the
quarterly dwell audit once its onboarding date (history/branches/README.md) is on or after
the cutoff below.
"""

DWELL_ONBOARDING_CUTOFF = "2034-04-01"


def onboarded_in_scope(onboarded_date, cutoff=DWELL_ONBOARDING_CUTOFF):
    """True once ``onboarded_date`` (YYYY-MM-DD) is on or after ``cutoff``."""
    return onboarded_date >= cutoff
