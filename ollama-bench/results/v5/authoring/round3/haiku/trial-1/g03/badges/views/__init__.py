"""View functions for the badge dashboard."""

VIEWS = ("grid", "detail", "compact", "activity", "owner")


def available():
    return list(VIEWS)
