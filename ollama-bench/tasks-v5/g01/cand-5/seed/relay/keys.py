"""Canonical entry-key and label operations.

These routines intentionally do not share a generic whitespace helper. Keys
and labels have the same release normalization, while source names are handled
by a different module and source aliases are a later step for keys.
"""

from .release_data import GLOBAL_KEY_ALIASES, SOURCE_KEY_ALIASES


def _edge_space(value):
    return value.strip(" ")


def canonical_key(source, key):
    value = _edge_space(key).casefold()
    value = GLOBAL_KEY_ALIASES.get(value, value)
    per_source = SOURCE_KEY_ALIASES.get(source, {})
    return per_source.get(value, value)


def canonical_label(label):
    return _edge_space(label).casefold()


def append_new_labels(existing, labels):
    """Append canonical nonempty labels not seen in this entry so far."""
    seen = set(existing)
    for label in labels:
        value = canonical_label(label)
        if value and value not in seen:
            existing.append(value)
            seen.add(value)


def key_examples():
    return [
        ("platform", " Err ", "error"),
        ("frontend", "WARN", "warning"),
        ("platform", "\tErr", "\terr"),
        ("platform", "  build  ", "build"),
    ]
