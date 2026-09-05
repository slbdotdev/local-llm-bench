"""Application façades for common consumer journeys."""

JOURNEYS = ("onboarding", "review", "release", "incident", "archive", "search")


def journeys():
    return list(JOURNEYS)
