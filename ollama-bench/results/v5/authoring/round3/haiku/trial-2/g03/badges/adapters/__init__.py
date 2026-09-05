"""Output adapters for external consumers."""

ADAPTERS = ("csv", "html", "plain", "slack", "terminal")


def available():
    return list(ADAPTERS)
