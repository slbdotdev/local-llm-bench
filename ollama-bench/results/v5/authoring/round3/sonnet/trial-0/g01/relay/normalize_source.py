"""Importer-facing source normalization review.

The production source adapter is intentionally a narrow function. This module
records the observations from each of the import paths so that a future change
does not accidentally broaden whitespace handling or make aliases recursive.
"""

from .release_data import SOURCE_ALIASES

ASCII_EDGE = " "


def importer_name(value):
    """Apply the release source rule to an already-valid string."""
    trimmed = value.strip(ASCII_EDGE)
    return SOURCE_ALIASES.get(trimmed, trimmed)


def same_bucket(left, right):
    """Whether two raw names participate in one output bucket."""
    return importer_name(left) == importer_name(right)


SOURCE_REVIEW = (
    (" core ", "platform"),
    (" svc ", "service"),
    ("web", "frontend"),
    ("ui", "frontend"),
    ("jobs", "worker"),
    ("batch", "worker"),
    (" platform ", "platform"),
    ("CORE", "CORE"),
    ("\tcore", "\tcore"),
    ("core\t", "core\t"),
    ("", ""),
)


def review_passes():
    return all(importer_name(raw) == expected for raw, expected in SOURCE_REVIEW)
