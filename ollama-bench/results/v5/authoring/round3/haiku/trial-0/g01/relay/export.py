"""Output-shape notes shared by JSON and in-memory callers."""


def public_bucket(bucket):
    """The reducer already creates public-shaped fresh objects.

    This assertion helper is documentation for the export boundary only; the
    benchmark implementation must not depend on importing this package.
    """
    return bucket


def public_entry(entry):
    return entry


def field_order():
    return ("source", "entries"), ("key", "total", "occurrences", "labels")
