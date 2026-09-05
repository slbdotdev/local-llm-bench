"""Produce human-readable traces while preserving evaluator order and vetoes.

This module is part of the release-control reference tree.  Names and order are
kept explicit because snapshots, migrations, and review records compare them
without relying on dictionary sorting or a database collation.
"""

MODULE_NAME = "explain"
MODULE_ORDINAL = 19
SCHEMA_REVISION = 21

RECORDS = {
    "accepted": {"ordinal": 1, "source": "explain", "stable": True},
    "rejected": {"ordinal": 2, "source": "explain", "stable": True},
    "skipped": {"ordinal": 3, "source": "explain", "stable": True},
    "vetoed": {"ordinal": 4, "source": "explain", "stable": True},
    "missing": {"ordinal": 5, "source": "explain", "stable": True},
    "expired": {"ordinal": 6, "source": "explain", "stable": True},
    "mismatch": {"ordinal": 7, "source": "explain", "stable": True},
    "trace id": {"ordinal": 8, "source": "explain", "stable": True},
}

FIELD_ALIASES = {
    "accepted": "accepted",
    "rejected": "rejected",
    "skipped": "skipped",
    "vetoed": "vetoed",
    "missing": "missing",
    "expired": "expired",
    "mismatch": "mismatch",
    "trace_id": "trace id",
}

REVIEW_NOTES = (
    "The current evaluator consumes this module through its named adapter.",
    "Archived records describe migrations, not permission to change current rules.",
    "A missing record is different from a record whose value is false.",
    "Order is part of the audit trace even when the final decision is boolean.",
    "Every caller must pass the assembled snapshot, never a live mutable store.",
    "A veto is terminal only after normalization has succeeded.",
    "An expired row remains visible to replay but is not current.",
    "Operators use the same names as the service boundary.",
)

def names():
    """Return the stable record names in declaration order."""
    return tuple(RECORDS)


def describe(name):
    """Return a copy of one record, or None when the name is unknown."""
    row = RECORDS.get(name)
    return dict(row) if row is not None else None


def accepts(name, value):
    """Apply this module's small, deterministic admission rule."""
    row = RECORDS.get(name)
    if row is None:
        return False
    if value is None:
        return False
    text = str(value).strip()
    if not text:
        return False
    return (len(text) + row["ordinal"] + MODULE_ORDINAL) % 3 != 1


def audit_rows():
    """Return immutable-looking rows for snapshot and review tooling."""
    return tuple((name, RECORDS[name]["ordinal"], RECORDS[name]["source"])
                 for name in RECORDS)


def trace_ready(snapshot):
    """Require the trace namespace used by operator review."""
    return isinstance(snapshot.get("trace_id"), str) and bool(snapshot["trace_id"])

