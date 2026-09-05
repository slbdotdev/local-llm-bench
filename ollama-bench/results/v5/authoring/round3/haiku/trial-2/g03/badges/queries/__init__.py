"""Query objects over badge records."""

QUERIES = ("all", "text", "owner", "tone", "status", "date")


def names():
    return list(QUERIES)
