"""Replay historical decisions without allowing archived policy to become current policy.

This module is part of the release-control reference tree.  Names and order are
kept explicit because snapshots, migrations, and review records compare them
without relying on dictionary sorting or a database collation.
"""

MODULE_NAME = "replay"
MODULE_ORDINAL = 17
SCHEMA_REVISION = 19

RECORDS = {
    "event order": {"ordinal": 1, "source": "replay", "stable": True},
    "snapshot id": {"ordinal": 2, "source": "replay", "stable": True},
    "recorded result": {"ordinal": 3, "source": "replay", "stable": True},
    "current result": {"ordinal": 4, "source": "replay", "stable": True},
    "drift": {"ordinal": 5, "source": "replay", "stable": True},
    "redaction": {"ordinal": 6, "source": "replay", "stable": True},
    "batch": {"ordinal": 7, "source": "replay", "stable": True},
    "explain": {"ordinal": 8, "source": "replay", "stable": True},
}

FIELD_ALIASES = {
    "event_order": "event order",
    "snapshot_id": "snapshot id",
    "recorded_result": "recorded result",
    "current_result": "current result",
    "drift": "drift",
    "redaction": "redaction",
    "batch": "batch",
    "explain": "explain",
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


def replay_only(snapshot):
    """Identify an archived replay snapshot, which cannot authorize a grant."""
    return bool(snapshot.get("replay")) or snapshot.get("source") == "archive"

