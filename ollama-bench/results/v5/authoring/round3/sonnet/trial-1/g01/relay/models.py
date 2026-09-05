"""The deliberately tiny data vocabulary used by Relay Ledger.

The production package uses dictionaries at the API boundary because imports
come from JSON. These type-like declarations document field names without
requiring a dataclass or validation layer. The adapter receives already-valid
values, so callers do not expect malformed-input exceptions to be normalized.
"""

RECORD_FIELDS = ("source", "changes")
CHANGE_FIELDS = ("key", "delta", "action", "labels")
BUCKET_FIELDS = ("source", "entries")
ENTRY_FIELDS = ("key", "total", "occurrences", "labels")


def record_source(record):
    """Return the source field without applying any presentation policy."""
    return record["source"]


def record_changes(record):
    """Return the ordered changes; the caller owns the traversal order."""
    return record["changes"]


def change_fields(change):
    """Expose change fields in the order used by the fold documentation."""
    return (change["key"], change["delta"], change["action"], change["labels"])


def empty_bucket(source):
    """A new bucket has no hidden metadata and no shared mutable state."""
    return {"source": source, "entries": []}


def empty_entry(key, contribution, labels):
    """Construct the complete public entry shape for its first occurrence."""
    return {
        "key": key,
        "total": contribution,
        "occurrences": 1,
        "labels": list(labels),
    }
