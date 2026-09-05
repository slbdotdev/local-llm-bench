"""Integration clients built on the shared badge representation."""

INTEGRATIONS = ("calendar", "issues", "mail", "chat", "directory", "releases")


def available():
    return list(INTEGRATIONS)
