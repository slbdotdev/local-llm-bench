"""Label accumulation belongs to accepted entry occurrences only."""

from .keys import append_new_labels


def labels_for(change):
    """Make a fresh canonical label list for the first accepted occurrence."""
    result = []
    append_new_labels(result, change["labels"])
    return result


def merge_labels(entry, change):
    """Update one existing entry without changing prior label order."""
    append_new_labels(entry["labels"], change["labels"])
