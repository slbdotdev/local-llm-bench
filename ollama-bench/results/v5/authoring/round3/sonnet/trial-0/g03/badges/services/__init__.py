"""Service layer for badge-backed application records."""

SERVICE_NAMES = ("cache", "search", "summary", "queue")


def names():
    return SERVICE_NAMES
