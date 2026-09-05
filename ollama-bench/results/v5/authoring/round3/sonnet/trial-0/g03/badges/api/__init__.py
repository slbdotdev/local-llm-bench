"""Internal API endpoint implementations."""

ENDPOINTS = ("list", "get", "create", "update", "delete", "stats")


def endpoints():
    return list(ENDPOINTS)
